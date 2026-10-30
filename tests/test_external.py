import hashlib
import json
from pathlib import Path

import pytest

from gamjagoon_skills_pack import external, installer
from gamjagoon_skills_pack.installer import SetupError

COMMIT = "a" * 40
ITEM = {
    "name": "mock-skill",
    "repository": "example/skills",
    "commit": COMMIT,
    "path": "skills/mock-skill",
    "license": "MIT",
    "license_path": "LICENSE",
    "license_url": "https://example.invalid/LICENSE",
}
FILES = {
    "skills/mock-skill/SKILL.md": (b"# Mock skill\n", "100644"),
    "skills/mock-skill/nested/helper.py": (b"raise RuntimeError('must not run')\n", "100755"),
    "LICENSE": (b"MIT License\n", "100644"),
}


def blob_sha(content: bytes) -> str:
    return hashlib.sha1(
        b"blob " + str(len(content)).encode() + b"\0" + content,
        usedforsecurity=False,
    ).hexdigest()


def tree_response(files=FILES, *, truncated: bool = False, extras=()) -> bytes:
    entries = [
        {
            "path": path,
            "type": "blob",
            "mode": mode,
            "size": len(content),
            "sha": blob_sha(content),
        }
        for path, (content, mode) in files.items()
    ]
    entries.extend(extras)
    return json.dumps({"truncated": truncated, "tree": entries}).encode()


def mock_github(monkeypatch, *, files=FILES, truncated=False, extras=(), response_overrides=None):
    bodies = {
        f"https://raw.githubusercontent.com/{ITEM['repository']}/{COMMIT}/{path}": content
        for path, (content, _mode) in files.items()
    }
    tree = tree_response(files, truncated=truncated, extras=extras)
    bodies.update(response_overrides or {})
    requested = []

    def request(url: str, _limit: int) -> bytes:
        requested.append(url)
        if url.endswith("?recursive=1"):
            return tree
        return bodies[url]

    monkeypatch.setattr(external, "_request", request)
    return requested


def test_catalog_has_expected_installable_and_link_only_entries() -> None:
    items = external.catalog()
    assert isinstance(items, list)
    assert any(
        item["name"] == "frontend-design" and item.get("installable", True) for item in items
    )
    link = next(item for item in items if item["name"] == "web-design-guidelines")
    assert link["installable"] is False


def test_download_returns_complete_subtree_license_modes_and_git_blob_checks(monkeypatch) -> None:
    requested = mock_github(monkeypatch)
    result = external.download_skill(ITEM)
    assert result == {
        "SKILL.md": (FILES["skills/mock-skill/SKILL.md"][0], 0o644),
        "nested/helper.py": (FILES["skills/mock-skill/nested/helper.py"][0], 0o755),
        "UPSTREAM-LICENSE": (FILES["LICENSE"][0], 0o644),
    }
    assert len(requested) == len(FILES) + 1


def test_add_skill_installs_files_and_exact_pinned_provenance_without_execution(
    tmp_path: Path, monkeypatch
) -> None:
    mock_github(monkeypatch)
    monkeypatch.setattr(external, "catalog", lambda: [ITEM])
    marker = tmp_path / "executed-marker"
    # The payload would create marker if imported or executed; installation treats it as bytes.
    payload = f"from pathlib import Path\nPath({str(marker)!r}).touch()\n".encode()
    files = {**FILES, "skills/mock-skill/nested/helper.py": (payload, "100755")}
    mock_github(monkeypatch, files=files)
    prior_lock = {"skills": {"other-skill": {"commit": "b" * 40}}}
    state = tmp_path / ".gamjagoon-skills-pack"
    state.mkdir()
    lock_path = state / "skills-lock.json"
    lock_path.write_text(json.dumps(prior_lock), encoding="utf-8")

    external.add_skill("mock-skill", tmp_path)

    destination = tmp_path / ".agents/skills/mock-skill"
    assert (destination / "SKILL.md").read_bytes() == FILES["skills/mock-skill/SKILL.md"][0]
    assert (destination / "nested/helper.py").read_bytes() == payload
    assert (destination / "nested/helper.py").stat().st_mode & 0o111
    assert (destination / "UPSTREAM-LICENSE").read_bytes() == FILES["LICENSE"][0]
    assert not marker.exists()
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    assert lock["skills"]["other-skill"] == prior_lock["skills"]["other-skill"]
    installed = lock["skills"]["mock-skill"]
    assert {key: installed[key] for key in ("repository", "commit", "path", "license")} == {
        key: ITEM[key] for key in ("repository", "commit", "path", "license")
    }
    assert installed["files"] == {
        relative: hashlib.sha256(content).hexdigest()
        for relative, (content, _mode) in {
            "SKILL.md": FILES["skills/mock-skill/SKILL.md"],
            "nested/helper.py": (payload, "100755"),
            "UPSTREAM-LICENSE": FILES["LICENSE"],
        }.items()
    }


def test_dry_run_has_no_network_or_project_changes(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "not-created"
    monkeypatch.setattr(external, "catalog", lambda: [ITEM])

    def forbidden(*_args, **_kwargs):
        raise AssertionError("dry run made a network request")

    monkeypatch.setattr(external, "_request", forbidden)
    external.add_skill("mock-skill", root, dry_run=True)
    assert not root.exists()


@pytest.mark.parametrize(
    "tree_kwargs",
    [
        {"truncated": True},
        {
            "response_overrides": {
                (
                    f"https://raw.githubusercontent.com/{ITEM['repository']}/"
                    f"{COMMIT}/skills/mock-skill/SKILL.md"
                ): b"corrupt"
            }
        },
    ],
)
def test_incomplete_tree_or_bad_blob_fails_before_project_writes(
    tmp_path: Path, monkeypatch, tree_kwargs
) -> None:
    monkeypatch.setattr(external, "catalog", lambda: [ITEM])
    mock_github(monkeypatch, **tree_kwargs)
    root = tmp_path / "project"
    root.mkdir()
    lock = root / ".gamjagoon-skills-pack/skills-lock.json"
    lock.parent.mkdir()
    lock.write_bytes(b'{"skills":{"keep":true}}\n')
    before = {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file()
    }
    with pytest.raises(SetupError):
        external.add_skill("mock-skill", root)
    after = {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file()
    }
    assert after == before
    assert not (root / ".agents").exists()


@pytest.mark.parametrize(
    "entry",
    [
        {
            "path": "skills/mock-skill/../escape",
            "type": "blob",
            "mode": "100644",
            "size": 0,
            "sha": blob_sha(b""),
        },
        {
            "path": "skills/mock-skill/link",
            "type": "blob",
            "mode": "120000",
            "size": 0,
            "sha": blob_sha(b""),
        },
    ],
)
def test_rejects_traversal_and_symlink_tree_entries(tmp_path: Path, monkeypatch, entry) -> None:
    monkeypatch.setattr(external, "catalog", lambda: [ITEM])
    mock_github(monkeypatch, extras=[entry])
    with pytest.raises(SetupError):
        external.add_skill("mock-skill", tmp_path)
    assert not (tmp_path / ".agents").exists()


def test_existing_skill_directory_is_preserved_without_download(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(external, "catalog", lambda: [ITEM])
    destination = tmp_path / ".agents/skills/mock-skill"
    destination.mkdir(parents=True)
    (destination / "local.txt").write_text("keep", encoding="utf-8")
    monkeypatch.setattr(
        external, "_request", lambda *_args: pytest.fail("existing skill triggered download")
    )
    with pytest.raises(SetupError):
        external.add_skill("mock-skill", tmp_path)
    assert (destination / "local.txt").read_text(encoding="utf-8") == "keep"
    assert list(destination.iterdir()) == [destination / "local.txt"]


def test_failed_add_removes_new_empty_skill_dirs_and_allows_retry(
    tmp_path: Path, monkeypatch
) -> None:
    mock_github(monkeypatch)
    monkeypatch.setattr(external, "catalog", lambda: [ITEM])
    skills_root = tmp_path / ".agents/skills"
    skills_root.mkdir(parents=True)
    destination = skills_root / ITEM["name"]
    real_atomic_write = installer.atomic_write
    target_writes = 0

    def fail_once_on_second_skill_file(path: Path, content: bytes, mode: int = 0o644) -> None:
        nonlocal target_writes
        if path.is_relative_to(destination):
            target_writes += 1
            if target_writes == 2:
                raise OSError("injected transient write failure")
        real_atomic_write(path, content, mode)

    monkeypatch.setattr(installer, "atomic_write", fail_once_on_second_skill_file)
    with pytest.raises(SetupError, match="복구했습니다"):
        external.add_skill("mock-skill", tmp_path)

    assert skills_root.is_dir()
    assert list(skills_root.iterdir()) == []
    assert not destination.exists()

    monkeypatch.setattr(installer, "atomic_write", real_atomic_write)
    external.add_skill("mock-skill", tmp_path)
    assert (destination / "SKILL.md").read_bytes() == FILES["skills/mock-skill/SKILL.md"][0]
    lock = json.loads(
        (tmp_path / ".gamjagoon-skills-pack/skills-lock.json").read_text(encoding="utf-8")
    )
    assert lock["skills"]["mock-skill"]["commit"] == COMMIT


def test_link_only_catalog_item_fails_clearly_without_changes(tmp_path: Path, monkeypatch) -> None:
    item = next(item for item in external.catalog() if item["name"] == "web-design-guidelines")
    monkeypatch.setattr(external, "catalog", lambda: [item])
    with pytest.raises(SetupError, match="원본 링크만 제공"):
        external.add_skill(item["name"], tmp_path)
    assert not tmp_path.exists() or list(tmp_path.iterdir()) == []
