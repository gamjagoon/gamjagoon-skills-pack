"""Explicit, pinned GitHub skill downloads. Project files and credentials are never read."""

from __future__ import annotations

import hashlib
import json
import re
import urllib.error
import urllib.request
from pathlib import Path, PurePosixPath

from .installer import (
    STATE_DIR,
    Change,
    SetupError,
    apply_changes,
    asset_root,
    read_existing,
    safe_path,
)

MAX_TREE_BYTES = 4_000_000
MAX_FILE_BYTES = 2_000_000
MAX_TOTAL_BYTES = 8_000_000
MAX_FILES = 128


def catalog() -> list[dict]:
    return json.loads(asset_root().joinpath("catalog.json").read_text(encoding="utf-8"))


def _request(url: str, limit: int) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "gamjagoon-skills-pack", "Accept": "application/vnd.github+json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            body = response.read(limit + 1)
    except (OSError, urllib.error.URLError) as exc:
        raise SetupError(f"스킬 다운로드에 실패했습니다: {exc}") from exc
    if len(body) > limit:
        raise SetupError(f"다운로드 크기 한도를 초과했습니다: {url}")
    return body


def _valid_relative(value: str) -> bool:
    return (
        bool(value)
        and not PurePosixPath(value).is_absolute()
        and "\\" not in value
        and all(part not in {"", ".", ".."} for part in value.split("/"))
    )


def download_skill(item: dict) -> dict[str, tuple[bytes, int]]:
    """Fetch the complete skill subtree and its license, checking each Git blob hash."""
    repository, commit, source = item["repository"], item["commit"], item["path"]
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise SetupError("잘못된 카탈로그 저장소입니다.")
    if not re.fullmatch(r"[0-9a-f]{40}", commit) or not _valid_relative(source):
        raise SetupError("카탈로그는 고정된 전체 커밋과 상대 경로를 사용해야 합니다.")
    try:
        tree = json.loads(
            _request(
                f"https://api.github.com/repos/{repository}/git/trees/{commit}?recursive=1",
                MAX_TREE_BYTES,
            )
        )
    except (ValueError, UnicodeError) as exc:
        raise SetupError("GitHub 파일 목록을 해석할 수 없습니다.") from exc
    if (
        not isinstance(tree, dict)
        or tree.get("truncated")
        or not isinstance(tree.get("tree"), list)
    ):
        raise SetupError("GitHub 파일 목록이 불완전합니다; 부분 설치하지 않습니다.")
    entries = tree["tree"]
    selected: dict[str, dict] = {}
    prefix = source.rstrip("/") + "/"
    for entry in entries:
        path = entry.get("path", "")
        if not path.startswith(prefix):
            continue
        relative = path[len(prefix) :]
        if not _valid_relative(relative):
            raise SetupError(f"외부 스킬의 경로가 올바르지 않습니다: {relative!r}")
        if entry.get("type") == "tree":
            continue
        if entry.get("type") != "blob" or entry.get("mode") not in {"100644", "100755"}:
            raise SetupError(f"외부 스킬에 링크 또는 지원하지 않는 파일이 있습니다: {path}")
        if relative in selected:
            raise SetupError(f"외부 스킬의 경로가 중복되었습니다: {relative}")
        selected[relative] = entry
    if "SKILL.md" not in selected:
        raise SetupError("선택한 경로에 SKILL.md가 없습니다.")
    license_path = item["license_path"]
    if not _valid_relative(license_path):
        raise SetupError("라이선스 경로가 올바르지 않습니다.")
    license_entry = next((entry for entry in entries if entry.get("path") == license_path), None)
    if license_entry is None:
        raise SetupError("고정 커밋에서 라이선스 파일을 찾을 수 없습니다.")
    if not license_path.startswith(prefix):
        if "UPSTREAM-LICENSE" in selected:
            raise SetupError("외부 라이선스 대상 이름이 충돌합니다.")
        selected["UPSTREAM-LICENSE"] = license_entry
    if len(selected) > MAX_FILES:
        raise SetupError("외부 스킬 파일 수 한도를 초과했습니다.")
    sizes = [entry.get("size", -1) for entry in selected.values()]
    if any(not isinstance(size, int) or size < 0 or size > MAX_FILE_BYTES for size in sizes):
        raise SetupError("외부 스킬 파일 크기가 잘못되었거나 한도를 초과했습니다.")
    if sum(sizes) > MAX_TOTAL_BYTES:
        raise SetupError("외부 스킬 전체 크기 한도를 초과했습니다.")
    result = {}
    for relative, entry in sorted(selected.items()):
        if entry.get("type") != "blob" or entry.get("mode") not in {"100644", "100755"}:
            raise SetupError("라이선스 파일이 일반 파일이 아닙니다.")
        body = _request(
            f"https://raw.githubusercontent.com/{repository}/{commit}/{entry['path']}",
            MAX_FILE_BYTES,
        )
        digest = hashlib.sha1(
            b"blob " + str(len(body)).encode() + b"\0" + body, usedforsecurity=False
        ).hexdigest()
        if len(body) != entry["size"] or digest != entry.get("sha"):
            raise SetupError(f"파일이 고정 커밋의 Git blob과 다릅니다: {entry['path']}")
        result[relative] = (body, 0o755 if entry["mode"] == "100755" else 0o644)
    return result


def add_skill(name: str, root: Path, *, dry_run: bool = False) -> None:
    item = next((item for item in catalog() if item["name"] == name), None)
    if item is None:
        raise SetupError(f"알 수 없는 스킬입니다: {name}; gsp skills list로 확인하세요.")
    print(f"SOURCE {item['repository']}@{item['commit']}/{item['path']}")
    print(f"LICENSE {item['license']} {item['license_url']}")
    if item.get("note"):
        print(f"NOTE {item['note']}")
    if not item.get("installable", True):
        raise SetupError("이 항목은 원본 링크만 제공합니다; 자동 다운로드 대상이 아닙니다.")
    if dry_run:
        print("DRY_RUN 네트워크 요청·파일·폴더 변경 없음")
        return
    destination = f".agents/skills/{name}"
    skill_file = safe_path(root, f"{destination}/SKILL.md")
    if skill_file.parent.exists():
        raise SetupError(f"기존 스킬 폴더를 보존합니다: {skill_file.parent}")
    lock_relative = f"{STATE_DIR}/skills-lock.json"
    lock_bytes, lock_mode = read_existing(root, lock_relative)
    try:
        lock = json.loads(lock_bytes) if lock_bytes is not None else {"skills": {}}
        if not isinstance(lock, dict) or not isinstance(lock.get("skills"), dict):
            raise ValueError("skills 객체가 없습니다.")
    except (ValueError, UnicodeError) as exc:
        raise SetupError("기존 skills-lock.json을 해석할 수 없습니다; 파일을 보존합니다.") from exc
    downloaded = download_skill(item)
    changes = []
    for relative, (content, mode) in downloaded.items():
        target = f"{destination}/{relative}"
        existing, _ = read_existing(root, target)
        if existing is not None:
            raise SetupError(f"다운로드 중 기존 파일이 생겼습니다: {target}")
        changes.append(Change(target, None, content, mode))
    lock["skills"][name] = {
        "repository": item["repository"],
        "commit": item["commit"],
        "path": item["path"],
        "license": item["license"],
        "files": {
            relative: hashlib.sha256(content).hexdigest()
            for relative, (content, _) in downloaded.items()
        },
    }
    changes.append(
        Change(
            lock_relative,
            lock_bytes,
            (json.dumps(lock, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(),
            lock_mode,
        )
    )
    apply_changes(root, changes)
    print(f"INSTALLED {name}: {len(downloaded)} files; 다운로드한 코드는 실행하지 않았습니다.")
