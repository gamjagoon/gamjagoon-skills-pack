"""Plan local file changes before applying them, preserving existing project content."""

from __future__ import annotations

import contextlib
import os
import stat
import tempfile
import uuid
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path, PurePosixPath

STATE_DIR = ".gamjagoon-skills-pack"
SKILL_DIR = ".agents/skills/timeboxed-workflow"
AGENT_FILE = ".codex/agents/gsp-reviewer.toml"
# Project-local contracts only; the installer never selects the running main model.
AGENT_ROLES = {
    "gsp-triage": ("gpt-6-luna", "low", "read-only"),
    "gsp-researcher": ("gpt-6-luna", "medium", "read-only"),
    "gsp-worker": ("gpt-6-luna", "medium", "workspace-write"),
    "gsp-integrator": ("gpt-6.1-sol", "medium", "workspace-write"),
    "gsp-debugger": ("gpt-6.1-sol", "high", "workspace-write"),
    "gsp-reviewer": ("gpt-6.1-sol", "medium", "read-only"),
}
AGENT_FILES = tuple(f".codex/agents/{name}.toml" for name in AGENT_ROLES)


class SetupError(Exception):
    """An expected setup error that can be shown without a traceback."""


@dataclass(frozen=True)
class Change:
    relative: str
    before: bytes | None
    after: bytes
    mode: int = 0o644

    @property
    def action(self) -> str:
        return "CREATE" if self.before is None else "UPDATE"


def asset_root():
    return files("gamjagoon_skills_pack").joinpath("assets")


def project_root(path: str | Path) -> Path:
    candidate = Path(path).expanduser().absolute()
    if candidate.is_symlink():
        raise SetupError(f"프로젝트 경로가 심볼릭 링크입니다: {candidate}")
    root = candidate.resolve()
    if root.exists() and not root.is_dir():
        raise SetupError(f"프로젝트 경로가 디렉터리가 아닙니다: {root}")
    return root


def global_codex_roots() -> set[Path]:
    roots = {Path.home() / ".codex"}
    custom_codex_home = os.environ.get("CODEX_HOME")
    if custom_codex_home:
        roots.add(Path(custom_codex_home).expanduser())
    return {path.resolve() for path in roots}


def ensure_project_scope(root: Path) -> None:
    """Refuse locations that turn project-local files into user-global Codex settings."""
    root = root.resolve()
    globals_ = global_codex_roots()
    if root == Path.home().resolve() or root in globals_ or (root / ".codex").resolve() in globals_:
        raise SetupError(
            "홈 또는 Codex 전역 설정 경로에는 적용하지 않습니다. 프로젝트 폴더를 지정하세요."
        )
    candidate = root / ".codex/config.toml"
    if candidate.is_file():
        for directory in globals_:
            global_config = directory / "config.toml"
            if global_config.is_file() and candidate.samefile(global_config):
                raise SetupError("프로젝트 설정이 전역 설정과 같은 파일입니다; 파일을 보존합니다.")


def safe_path(root: Path, relative: str) -> Path:
    parts = PurePosixPath(relative).parts
    if (
        not parts
        or PurePosixPath(relative).is_absolute()
        or any(part in {"", ".", ".."} for part in relative.split("/"))
        or "\\" in relative
    ):
        raise SetupError(f"허용되지 않은 상대 경로입니다: {relative!r}")
    current = root
    for index, part in enumerate(parts):
        current /= part
        if current.is_symlink():
            raise SetupError(f"관리 경로의 심볼릭 링크는 지원하지 않습니다: {current}")
        if current.exists():
            if index < len(parts) - 1 and not current.is_dir():
                raise SetupError(f"상위 경로가 디렉터리가 아닙니다: {current}")
            if index == len(parts) - 1 and not current.is_file():
                raise SetupError(f"대상 경로가 일반 파일이 아닙니다: {current}")
    return current


def read_existing(root: Path, relative: str) -> tuple[bytes | None, int]:
    target = safe_path(root, relative)
    if not target.exists():
        return None, 0o644
    return target.read_bytes(), stat.S_IMODE(target.stat().st_mode)


def file_change(
    root: Path, relative: str, data: bytes, *, overwrite: bool = False
) -> Change | None:
    previous, mode = read_existing(root, relative)
    if previous == data:
        return None
    if previous is not None and not overwrite:
        raise SetupError(
            f"기존 파일과 내용이 다릅니다: {relative}\n"
            "내용을 확인한 뒤 --overwrite를 지정하면 백업 후 교체합니다."
        )
    return Change(relative, previous, data, mode)


def managed_change(
    root: Path,
    relative: str,
    content: bytes,
    *,
    comment: str,
    overwrite: bool,
) -> Change | None:
    previous, mode = read_existing(root, relative)
    original = previous or b""
    begin = f"{comment} GAMJAGOON-SKILLS-PACK:START".encode()
    end = f"{comment} GAMJAGOON-SKILLS-PACK:END".encode()
    if comment == "<!--":
        begin += b" -->"
        end += b" -->"
    block = begin + b"\n" + content.rstrip(b"\n") + b"\n" + end
    if original.count(begin) != original.count(end) or original.count(begin) > 1:
        raise SetupError(f"관리 블록이 잘못되었거나 중복되었습니다: {relative}")
    if begin in original:
        start = original.index(begin)
        stop = original.index(end) + len(end)
        if stop <= start:
            raise SetupError(f"관리 블록 순서가 잘못되었습니다: {relative}")
        if original[start:stop] == block:
            return None
        if not overwrite:
            raise SetupError(f"기존 관리 블록이 다릅니다: {relative}; 확인 후 --overwrite 사용")
        updated = original[:start] + block + original[stop:]
    else:
        separator = b"" if not original else (b"\n" if original.endswith(b"\n") else b"\n\n")
        updated = original + separator + block + b"\n"
    return Change(relative, previous, updated, mode)


def _resource_files(directory, prefix: str = ""):
    for child in sorted(directory.iterdir(), key=lambda item: item.name):
        relative = f"{prefix}{child.name}"
        if child.is_dir():
            yield from _resource_files(child, relative + "/")
        elif child.is_file():
            yield relative, child.read_bytes()


def plan_init(root: Path, *, minutes: int = 180, overwrite: bool = False) -> list[Change]:
    ensure_project_scope(root)
    if minutes <= 0:
        raise SetupError("--minutes는 1 이상의 실제 제작 시간이어야 합니다.")
    # Guard local state before planning any writes, even if no backup is needed yet.
    safe_path(root, f"{STATE_DIR}/install.lock")
    assets = asset_root()
    changes = [
        managed_change(
            root,
            "AGENTS.md",
            assets.joinpath("agents.fragment.md").read_bytes(),
            comment="<!--",
            overwrite=overwrite,
        ),
        managed_change(
            root,
            ".gitignore",
            f"{STATE_DIR}/\n".encode(),
            comment="#",
            overwrite=overwrite,
        ),
    ]
    task, _ = read_existing(root, "TASK.md")
    if task is None:
        changes.append(
            file_change(
                root,
                "TASK.md",
                assets.joinpath("task.md")
                .read_bytes()
                .replace(b"{{MINUTES}}", str(minutes).encode()),
            )
        )
    for name in AGENT_ROLES:
        resource = (
            assets.joinpath("reviewer.toml")
            if name == "gsp-reviewer"
            else assets.joinpath("agents", f"{name}.toml")
        )
        changes.append(
            file_change(
                root, f".codex/agents/{name}.toml", resource.read_bytes(), overwrite=overwrite
            )
        )
    for relative, data in _resource_files(assets.joinpath("workflow")):
        changes.append(file_change(root, f"{SKILL_DIR}/{relative}", data, overwrite=overwrite))
    return [change for change in changes if change is not None]


def atomic_write(path: Path, content: bytes, mode: int = 0o644) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".gsp-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    finally:
        with contextlib.suppress(FileNotFoundError):
            os.unlink(temporary)


def apply_changes(root: Path, changes: list[Change]) -> list[str]:
    """Apply a preflighted plan; restore previously written file contents on failure."""
    if not changes:
        return []
    if len({change.relative for change in changes}) != len(changes):
        raise SetupError("설치 대상 경로가 중복되었습니다.")
    lock_path = safe_path(root, f"{STATE_DIR}/install.lock")
    new_directories: set[Path] = set()
    for parent in [
        lock_path.parent,
        *(safe_path(root, change.relative).parent for change in changes),
    ]:
        while parent == root or root in parent.parents:
            if not parent.exists():
                new_directories.add(parent)
            if parent == root:
                break
            parent = parent.parent
    root.mkdir(parents=True, exist_ok=True)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        lock_fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise SetupError(f"다른 설치가 진행 중이거나 잠금이 남아 있습니다: {lock_path}") from exc
    os.close(lock_fd)
    backups: list[str] = []
    written: list[Change] = []
    backup_id = uuid.uuid4().hex
    failed = True
    try:
        for change in changes:
            current, _ = read_existing(root, change.relative)
            if current != change.before:
                raise SetupError(
                    f"계획 후 파일이 변경되었습니다: {change.relative}; 다시 실행하세요."
                )
        for change in changes:
            current, _ = read_existing(root, change.relative)
            if current != change.before:
                raise SetupError(f"설치 중 파일이 변경되었습니다: {change.relative}")
            if change.before is not None:
                relative = f"{STATE_DIR}/backups/{backup_id}/{change.relative}"
                backup = safe_path(root, relative)
                atomic_write(backup, change.before, 0o600)
                backups.append(relative)
            target = safe_path(root, change.relative)
            atomic_write(target, change.after, change.mode)
            written.append(change)
        failed = False
    except Exception as exc:
        recovery_errors = []
        for change in reversed(written):
            try:
                target = safe_path(root, change.relative)
                if target.read_bytes() != change.after:
                    raise SetupError("다른 프로세스의 변경을 덮어쓸 수 없습니다.")
                if change.before is None:
                    target.unlink()
                else:
                    atomic_write(target, change.before, change.mode)
            except Exception as recovery:
                recovery_errors.append(f"{change.relative}: {recovery}")
        if recovery_errors:
            raise SetupError(
                f"설치 실패: {exc}\n일부 복구 실패: {'; '.join(recovery_errors)}\n"
                f"백업 확인: {root / STATE_DIR / 'backups' / backup_id}"
            ) from exc
        raise SetupError(f"설치 실패; 작성한 파일 내용을 복구했습니다: {exc}") from exc
    finally:
        lock_path.unlink(missing_ok=True)
        if failed:
            for directory in sorted(
                new_directories, key=lambda item: len(item.parts), reverse=True
            ):
                # rmdir preserves pre-existing directories and concurrent files automatically.
                with contextlib.suppress(OSError):
                    directory.rmdir()
    return backups
