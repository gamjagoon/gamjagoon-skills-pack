from pathlib import Path

import pytest

from gamjagoon_skills_pack import installer
from gamjagoon_skills_pack.installer import Change, SetupError


def snapshot(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file()
    }


def test_project_root_and_minutes_validation(tmp_path: Path) -> None:
    assert installer.project_root(tmp_path / "new") == (tmp_path / "new").absolute()
    with pytest.raises(SetupError):
        installer.plan_init(tmp_path, minutes=0)


def test_init_refuses_home_before_creating_project_files(tmp_path: Path, monkeypatch) -> None:
    home = tmp_path / "fake-home"
    home.mkdir()
    monkeypatch.setattr(Path, "home", lambda: home)

    with pytest.raises(SetupError):
        installer.plan_init(home)
    assert list(home.iterdir()) == []


@pytest.mark.parametrize("relative", ["../escape", "/absolute", "a/../../escape", "a\\b"])
def test_safe_path_rejects_traversal(tmp_path: Path, relative: str) -> None:
    with pytest.raises(SetupError):
        installer.safe_path(tmp_path, relative)


def test_project_root_and_managed_path_reject_symlinks(tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    link = tmp_path / "project-link"
    link.symlink_to(outside, target_is_directory=True)
    with pytest.raises(SetupError):
        installer.project_root(link)

    root = tmp_path / "project"
    root.mkdir()
    (root / ".agents").symlink_to(outside, target_is_directory=True)
    with pytest.raises(SetupError):
        installer.plan_init(root)


def test_plan_init_preserves_unmanaged_content_and_task(tmp_path: Path) -> None:
    root = tmp_path / "project"
    root.mkdir()
    agents = b"# Existing guidance\nkeep this\n"
    ignore = b"*.local\n"
    task = b"user-owned task\n"
    config = b'model = "user-choice"\n'
    (root / "AGENTS.md").write_bytes(agents)
    (root / ".gitignore").write_bytes(ignore)
    (root / "TASK.md").write_bytes(task)
    (root / ".codex/agents").mkdir(parents=True)
    (root / ".codex/agents/gsp-reviewer.toml").write_bytes(config)

    with pytest.raises(SetupError):
        installer.plan_init(root)
    assert (root / "AGENTS.md").read_bytes() == agents
    assert (root / ".gitignore").read_bytes() == ignore
    assert (root / "TASK.md").read_bytes() == task
    assert (root / ".codex/agents/gsp-reviewer.toml").read_bytes() == config

    changes = installer.plan_init(root, overwrite=True)
    change_by_path = {change.relative: change for change in changes}
    assert change_by_path["AGENTS.md"].before.startswith(agents)
    assert change_by_path[".gitignore"].before == ignore
    assert "TASK.md" not in change_by_path
    assert ".codex/agents/gsp-reviewer.toml" in change_by_path


def test_dry_run_creates_nothing_and_does_not_use_network(tmp_path: Path, monkeypatch) -> None:
    from gamjagoon_skills_pack import cli

    root = tmp_path / "absent"

    def network_forbidden(*args, **kwargs):
        raise AssertionError("dry-run attempted network access")

    monkeypatch.setattr("urllib.request.urlopen", network_forbidden)
    monkeypatch.setattr("socket.create_connection", network_forbidden)
    assert cli.main(["init", str(root), "--dry-run"]) == 0
    assert not root.exists()


def test_init_is_idempotent_and_keeps_unrelated_codex_config(tmp_path: Path) -> None:
    from gamjagoon_skills_pack import cli

    root = tmp_path / "project"
    root.mkdir()
    config = b"[settings]\nvalue = 42\n"
    (root / ".codex").mkdir()
    (root / ".codex/config.toml").write_bytes(config)
    assert cli.main(["init", str(root), "--minutes", "90"]) == 0
    after_first = snapshot(root)
    assert (root / ".codex/config.toml").read_bytes() == config
    assert cli.main(["init", str(root), "--minutes", "90"]) == 0
    assert snapshot(root) == after_first


def test_overwrite_backs_up_replaced_content(tmp_path: Path) -> None:
    root = tmp_path / "project"
    root.mkdir()
    target = root / "TASK.md"
    target.write_bytes(b"old\n")
    change = Change("TASK.md", b"old\n", b"new\n")
    backups = installer.apply_changes(root, [change])
    assert target.read_bytes() == b"new\n"
    assert len(backups) == 1
    assert (root / backups[0]).read_bytes() == b"old\n"


def test_stale_plan_refuses_to_write(tmp_path: Path) -> None:
    root = tmp_path / "project"
    root.mkdir()
    (root / "TASK.md").write_bytes(b"planned\n")
    changes = installer.plan_init(root)
    target = root / ".codex/agents/gsp-reviewer.toml"
    target.parent.mkdir(parents=True)
    target.write_bytes(b"changed after plan\n")
    before = snapshot(root)
    with pytest.raises(SetupError, match="계획 후 파일이 변경"):
        installer.apply_changes(root, changes)
    assert snapshot(root) == before


def test_write_failure_restores_previously_written_files(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "project"
    root.mkdir()
    (root / "one").write_bytes(b"old-one")
    changes = [Change("one", b"old-one", b"new-one"), Change("two", None, b"new-two")]
    real_atomic_write = installer.atomic_write
    calls = 0

    def fail_second_write(path: Path, content: bytes, mode: int = 0o644) -> None:
        nonlocal calls
        calls += 1
        # First call backs up one, second replaces one, third attempts two.
        if calls == 3:
            raise OSError("injected write failure")
        real_atomic_write(path, content, mode)

    monkeypatch.setattr(installer, "atomic_write", fail_second_write)
    with pytest.raises(SetupError, match="복구했습니다"):
        installer.apply_changes(root, changes)
    assert (root / "one").read_bytes() == b"old-one"
    assert not (root / "two").exists()


def test_conflicting_targets_abort_before_any_project_change(tmp_path: Path) -> None:
    root = tmp_path / "project"
    root.mkdir()
    (root / "TASK.md").write_bytes(b"preserve me")
    (root / ".codex/agents/gsp-reviewer.toml").parent.mkdir(parents=True)
    (root / ".codex/agents/gsp-reviewer.toml").write_bytes(b"conflicting reviewer")
    before = snapshot(root)
    with pytest.raises(SetupError):
        installer.plan_init(root)
    assert snapshot(root) == before
