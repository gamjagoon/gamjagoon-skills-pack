import tomllib
from pathlib import Path

import pytest

from gamjagoon_skills_pack import cli
from gamjagoon_skills_pack.installer import SetupError, apply_changes
from gamjagoon_skills_pack.keyboard import CONFIG_FILE, plan_keyboard


def read_config(root: Path) -> dict:
    return tomllib.loads((root / CONFIG_FILE).read_text(encoding="utf-8"))


def test_newline_profile_creates_expected_project_local_toml(tmp_path: Path) -> None:
    changes = plan_keyboard(tmp_path)
    apply_changes(tmp_path, changes)
    config = read_config(tmp_path)
    assert config["tui"]["keymap"]["composer"]["submit"] == ["alt-enter", "ctrl-enter"]
    assert config["tui"]["keymap"]["editor"]["insert_newline"] == [
        "enter",
        "ctrl-j",
        "shift-enter",
    ]
    assert (tmp_path / ".gitignore").read_text(encoding="utf-8").find(
        ".gamjagoon-skills-pack/"
    ) >= 0


def test_cli_dry_run_creates_no_project_files(tmp_path: Path, capsys) -> None:
    root = tmp_path / "not-created"
    assert cli.main(["keyboard", str(root), "--dry-run"]) == 0
    assert "DRY_RUN" in capsys.readouterr().out
    assert not root.exists()


def test_existing_values_comments_and_unrelated_keymap_entries_survive(tmp_path: Path) -> None:
    root = tmp_path / "project"
    root.mkdir()
    source = (
        "# Keep this comment\nmodel = 'gpt-local'\n"
        "approval_policy = 'never'\n"
        "[mcp_servers.sample]\ncommand = 'local-tool'\n"
        "[tui.keymap.composer]\nhistory_search_next = ['ctrl-s']\n"
        "[tui.keymap.editor]\ncustom_action = ['ctrl-k'] # editor note\n"
        "insert_newline = ['alt-enter'] # replaced setting\n"
    )
    (root / CONFIG_FILE).parent.mkdir()
    (root / CONFIG_FILE).write_text(source, encoding="utf-8")

    apply_changes(root, plan_keyboard(root))

    result_text = (root / CONFIG_FILE).read_text(encoding="utf-8")
    result = tomllib.loads(result_text)
    original = tomllib.loads(source)
    for key in ("model", "approval_policy", "mcp_servers"):
        assert result[key] == original[key]
    assert result["tui"]["keymap"]["editor"]["custom_action"] == ["ctrl-k"]
    assert result["tui"]["keymap"]["composer"]["history_search_next"] == ["ctrl-s"]
    assert result_text.startswith("# Keep this comment\nmodel = 'gpt-local'\n")
    assert "# editor note" in result_text


def test_ordinary_tables_and_multiline_array_update_without_losing_other_values(
    tmp_path: Path,
) -> None:
    root = tmp_path / "project"
    root.mkdir()
    config_path = root / CONFIG_FILE
    config_path.parent.mkdir()
    config_path.write_text(
        "[ui]\ntheme = 'dark'\n[tui.keymap.composer]\n"
        "submit = [\n  'ctrl-x', # old mapping\n  'ctrl-y',\n]\n"
        "[tui.keymap.editor]\ninsert_newline = ['ctrl-n']\nother = 'preserve'\n",
        encoding="utf-8",
    )

    apply_changes(root, plan_keyboard(root))

    config = read_config(root)
    assert config["ui"]["theme"] == "dark"
    assert config["tui"]["keymap"]["editor"]["other"] == "preserve"
    assert config["tui"]["keymap"]["composer"]["submit"] == ["alt-enter", "ctrl-enter"]
    assert config["tui"]["keymap"]["editor"]["insert_newline"] == [
        "enter",
        "ctrl-j",
        "shift-enter",
    ]


def test_crlf_is_preserved_outside_targeted_assignments(tmp_path: Path) -> None:
    root = tmp_path / "project"
    root.mkdir()
    config_path = root / CONFIG_FILE
    config_path.parent.mkdir()
    config_path.write_bytes(
        b"# Keep CRLF\r\n[ui]\r\ntheme = 'dark'\r\n[tui.keymap.composer]\r\n"
        b"submit = ['ctrl-x']\r\n[tui.keymap.editor]\r\ninsert_newline = ['ctrl-n']\r\n"
    )

    apply_changes(root, plan_keyboard(root))

    result = config_path.read_bytes()
    assert b"# Keep CRLF\r\n[ui]\r\ntheme = 'dark'\r\n" in result
    assert b"\n" not in result.replace(b"\r\n", b"")
    assert read_config(root)["ui"]["theme"] == "dark"


def test_repeated_profile_is_idempotent_and_backups_original_config(tmp_path: Path) -> None:
    root = tmp_path / "project"
    root.mkdir()
    config = root / CONFIG_FILE
    config.parent.mkdir()
    original = b"model = 'keep'\n[tui.keymap.composer]\nsubmit = ['ctrl-x']\n"
    config.write_bytes(original)

    first_plan = plan_keyboard(root)
    backups = apply_changes(root, first_plan)
    assert len(backups) == 1
    assert (root / backups[0]).read_bytes() == original
    stable = config.read_bytes()
    assert plan_keyboard(root) == []
    assert config.read_bytes() == stable


def test_switching_profiles_sets_submit_and_newline_bindings(tmp_path: Path) -> None:
    apply_changes(tmp_path, plan_keyboard(tmp_path, enter="newline"))
    apply_changes(tmp_path, plan_keyboard(tmp_path, enter="submit"))
    config = read_config(tmp_path)
    assert config["tui"]["keymap"]["composer"]["submit"] == ["enter", "ctrl-m"]
    assert config["tui"]["keymap"]["editor"]["insert_newline"] == [
        "ctrl-j",
        "shift-enter",
        "alt-enter",
    ]


@pytest.mark.parametrize(
    "contents",
    [
        "[tui\ninvalid = true\n",
        "[tui]\nkeymap = 'not a table'\n",
        "tui = { keymap = { composer = { submit = ['ctrl-x'] } } }\n",
    ],
)
def test_invalid_or_unsupported_toml_fails_without_file_changes(
    tmp_path: Path, contents: str
) -> None:
    root = tmp_path / "project"
    root.mkdir()
    config = root / CONFIG_FILE
    config.parent.mkdir()
    original = contents.encode()
    config.write_bytes(original)
    with pytest.raises(SetupError):
        plan_keyboard(root)
    assert config.read_bytes() == original
    assert not (root / ".gitignore").exists()


def test_symlink_config_is_refused_without_touching_link_target(tmp_path: Path) -> None:
    root = tmp_path / "project"
    root.mkdir()
    outside = tmp_path / "outside.toml"
    original = b"model = 'untouched'\n"
    outside.write_bytes(original)
    (root / ".codex").mkdir()
    (root / CONFIG_FILE).symlink_to(outside)
    with pytest.raises(SetupError):
        plan_keyboard(root)
    assert outside.read_bytes() == original


def test_invalid_profile_refuses_without_changes(tmp_path: Path) -> None:
    with pytest.raises(SetupError):
        plan_keyboard(tmp_path, enter="custom")
    assert not tmp_path.exists() or list(tmp_path.iterdir()) == []


def test_cli_keyboard_from_home_refuses_global_config_without_changes(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    home = tmp_path / "fake-home"
    config = home / ".codex/config.toml"
    config.parent.mkdir(parents=True)
    original = b"model = 'global-choice'\n"
    config.write_bytes(original)
    monkeypatch.setattr(Path, "home", lambda: home)
    monkeypatch.chdir(home)

    assert cli.main(["keyboard"]) == 1
    assert "ERROR" in capsys.readouterr().err
    assert config.read_bytes() == original
    assert not (home / ".gitignore").exists()


def test_keyboard_refuses_active_custom_codex_home_project_collision(
    tmp_path: Path, monkeypatch
) -> None:
    root = tmp_path / "project"
    global_codex = root / ".codex"
    config = global_codex / "config.toml"
    config.parent.mkdir(parents=True)
    original = b"model = 'custom-global'\n"
    config.write_bytes(original)
    monkeypatch.setattr(
        "gamjagoon_skills_pack.installer.global_codex_roots", lambda: {global_codex}
    )

    with pytest.raises(SetupError):
        plan_keyboard(root)
    assert config.read_bytes() == original
    assert not (root / ".gitignore").exists()


def test_keyboard_refuses_config_hardlinked_to_active_global_file(
    tmp_path: Path, monkeypatch
) -> None:
    root = tmp_path / "project"
    project_config = root / CONFIG_FILE
    project_config.parent.mkdir(parents=True)
    original = b"model = 'shared-global-file'\n"
    project_config.write_bytes(original)
    global_codex = tmp_path / "active-codex-home"
    global_codex.mkdir()
    global_config = global_codex / "config.toml"
    global_config.hardlink_to(project_config)
    monkeypatch.setattr(
        "gamjagoon_skills_pack.installer.global_codex_roots", lambda: {global_codex}
    )

    with pytest.raises(SetupError):
        plan_keyboard(root)
    assert project_config.read_bytes() == original
    assert global_config.read_bytes() == original
    assert not (root / ".gitignore").exists()
