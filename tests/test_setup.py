from pathlib import Path

import pytest

from gamjagoon_skills_pack import cli, installer
from gamjagoon_skills_pack.installer import AGENT_FILE, SKILL_DIR, SetupError, apply_changes
from gamjagoon_skills_pack.setup import plan_setup


def test_setup_composes_one_plan_and_installs_every_component(tmp_path: Path) -> None:
    changes = plan_setup(tmp_path)
    paths = [change.relative for change in changes]
    assert len(paths) == len(set(paths))
    apply_changes(tmp_path, changes)
    assert (tmp_path / AGENT_FILE).is_file()
    assert (tmp_path / SKILL_DIR / "references/handoff.md").is_file()
    assert "180" in (tmp_path / "TASK.md").read_text()
    assert 'submit = ["alt-enter", "ctrl-enter"]' in (tmp_path / ".codex/config.toml").read_text()
    assert plan_setup(tmp_path) == []


def test_setup_dry_run_has_no_side_effects_or_network(tmp_path: Path, monkeypatch) -> None:
    target = tmp_path / "new-project"

    def no_network(*args, **kwargs):
        raise AssertionError("setup must not access the network")

    monkeypatch.setattr("urllib.request.urlopen", no_network)
    assert cli.main(["setup", str(target), "--dry-run"]) == 0
    assert not target.exists()
    assert cli.main(["setup", str(target)]) == 0


def test_keyboard_conflict_prevents_partial_workflow_install(tmp_path: Path) -> None:
    config = tmp_path / ".codex/config.toml"
    config.parent.mkdir()
    config.write_text("this is not TOML")
    original = config.read_bytes()
    assert cli.main(["setup", str(tmp_path)]) == 1
    assert config.read_bytes() == original
    assert not (tmp_path / "AGENTS.md").exists()
    assert not (tmp_path / "TASK.md").exists()
    assert not (tmp_path / ".gamjagoon-skills-pack").exists()


def test_setup_no_keyboard_preserves_user_input_settings(tmp_path: Path) -> None:
    config = tmp_path / ".codex/config.toml"
    config.parent.mkdir()
    config.write_text('model = "existing-model"\n')
    assert cli.main(["setup", str(tmp_path), "--no-keyboard", "--minutes", "95"]) == 0
    assert config.read_text() == 'model = "existing-model"\n'
    assert "95" in (tmp_path / "TASK.md").read_text()


def test_setup_keyboard_write_failure_rolls_back_workflow(tmp_path: Path, monkeypatch) -> None:
    instructions = tmp_path / "AGENTS.md"
    instructions.write_bytes(b"Existing user instructions\n")
    changes = plan_setup(tmp_path)
    write = installer.atomic_write
    failed = False

    def fail_keyboard_once(path, content, mode=0o644):
        nonlocal failed
        if path == tmp_path / ".codex/config.toml" and not failed:
            failed = True
            raise OSError("injected keyboard failure")
        return write(path, content, mode)

    monkeypatch.setattr(installer, "atomic_write", fail_keyboard_once)
    with pytest.raises(SetupError):
        apply_changes(tmp_path, changes)
    assert instructions.read_bytes() == b"Existing user instructions\n"
    assert not (tmp_path / "TASK.md").exists()
    assert not (tmp_path / AGENT_FILE).exists()
    assert not (tmp_path / SKILL_DIR).exists()
    assert not (tmp_path / ".codex/config.toml").exists()


def test_setup_overwrite_handles_shared_ignore_block(tmp_path: Path) -> None:
    ignored = tmp_path / ".gitignore"
    original = (
        b"user-pattern\n# GAMJAGOON-SKILLS-PACK:START\nold-state/\n# GAMJAGOON-SKILLS-PACK:END\n"
    )
    ignored.write_bytes(original)
    assert cli.main(["setup", str(tmp_path), "--overwrite"]) == 0
    assert ignored.read_bytes().startswith(b"user-pattern\n")
    backups = list((tmp_path / ".gamjagoon-skills-pack/backups").rglob(".gitignore"))
    assert len(backups) == 1
    assert backups[0].read_bytes() == original


def test_setup_refuses_home_as_target(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    assert cli.main(["setup", str(tmp_path)]) == 1
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("dry_run", [False, True])
def test_empty_preserved_task_is_rejected_before_any_changes(tmp_path: Path, dry_run: bool) -> None:
    (tmp_path / "TASK.md").touch()
    arguments = ["setup", str(tmp_path)]
    if dry_run:
        arguments.append("--dry-run")
    assert cli.main(arguments) == 1
    assert list(tmp_path.iterdir()) == [tmp_path / "TASK.md"]
    assert (tmp_path / "TASK.md").read_bytes() == b""
