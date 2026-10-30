import tomllib
from pathlib import Path

import pytest

from gamjagoon_skills_pack import cli
from gamjagoon_skills_pack.installer import (
    AGENT_FILE,
    AGENT_FILES,
    AGENT_ROLES,
    SKILL_DIR,
    apply_changes,
    plan_init,
)


@pytest.mark.parametrize("stage", cli.STAGES)
def test_prompt_stage_prints_readable_korean_content(stage: str, capsys) -> None:
    assert cli.main(["prompt", stage]) == 0
    output = capsys.readouterr().out
    assert output.strip()
    assert "\ufffd" not in output
    assert any("가" <= char <= "힣" for char in output)


def test_prompt_without_stage_lists_all_stages(capsys) -> None:
    assert cli.main(["prompt"]) == 0
    assert capsys.readouterr().out.splitlines() == list(cli.STAGES)


def test_install_plan_contains_every_prompt_resource(tmp_path: Path) -> None:
    changes = plan_init(tmp_path)
    paths = {change.relative for change in changes}
    for stage in cli.STAGES:
        assert f"{SKILL_DIR}/references/{stage}.md" in paths
    assert f"{SKILL_DIR}/SKILL.md" in paths
    assert AGENT_FILE in paths


def test_installed_files_include_task_and_explicit_read_only_reviewer(tmp_path: Path) -> None:
    changes = plan_init(tmp_path, minutes=135)
    apply_changes(tmp_path, changes)
    task = (tmp_path / "TASK.md").read_text(encoding="utf-8")
    assert "135" in task
    reviewer = tomllib.loads((tmp_path / AGENT_FILE).read_text(encoding="utf-8"))
    assert reviewer["sandbox_mode"] == "read-only"
    assert reviewer["model"] == "gpt-6.1-sol"
    assert reviewer["model_reasoning_effort"] == "medium"
    assert "service_tier" not in reviewer


def test_doctor_reports_static_check_and_runtime_not_run(
    tmp_path: Path, capsys, monkeypatch
) -> None:
    apply_changes(tmp_path, plan_init(tmp_path))
    monkeypatch.setattr("shutil.which", lambda _name: None)
    assert cli.main(["doctor", str(tmp_path)]) == 0
    output = capsys.readouterr().out
    assert "PASS agent TOML gsp-reviewer" in output
    assert "NOT_RUN" in output
    assert "실제 Codex" in output
    assert "WARN command" in output


@pytest.mark.parametrize(
    ("before", "after"),
    [
        ('model = "gpt-6.1-sol"', 'model = "unsupported-model"'),
        ('model_reasoning_effort = "medium"', 'model_reasoning_effort = "ultra"'),
        ('sandbox_mode = "read-only"', 'sandbox_mode = "read-only"\nservice_tier = "priority"'),
        ('name = "gsp-reviewer"', 'name = "wrong-role"'),
        ('model = "gpt-6.1-sol"', ""),
        ('model_reasoning_effort = "medium"', ""),
    ],
)
def test_doctor_rejects_unsupported_or_missing_role_settings(
    tmp_path: Path, capsys, before: str, after: str
) -> None:
    apply_changes(tmp_path, plan_init(tmp_path))
    reviewer = tmp_path / AGENT_FILE
    reviewer.write_text(reviewer.read_text().replace(before, after))
    assert cli.main(["doctor", str(tmp_path)]) == 1
    assert "FAIL agent TOML gsp-reviewer" in capsys.readouterr().out


@pytest.mark.parametrize("reference", ["verify", "parallel-work", "model-routing"])
def test_doctor_detects_missing_prompt_resource(tmp_path: Path, capsys, reference: str) -> None:
    apply_changes(tmp_path, plan_init(tmp_path))
    (tmp_path / SKILL_DIR / "references" / f"{reference}.md").unlink()
    assert cli.main(["doctor", str(tmp_path)]) == 1
    assert "FAIL missing/empty" in capsys.readouterr().out


def test_prompt_rejects_unknown_stage() -> None:
    with pytest.raises(SystemExit) as error:
        cli.main(["prompt", "unknown"])
    assert error.value.code == 2


@pytest.mark.parametrize("relative", AGENT_FILES)
def test_doctor_detects_missing_role(tmp_path: Path, capsys, relative: str) -> None:
    apply_changes(tmp_path, plan_init(tmp_path))
    (tmp_path / relative).unlink()
    assert cli.main(["doctor", str(tmp_path)]) == 1
    assert f"FAIL missing/empty {relative}" in capsys.readouterr().out


@pytest.mark.parametrize(
    "content",
    [
        "not TOML",
        'name = "gsp-worker"',
        'name = "gsp-worker"\ndescription = "work"\ndeveloper_instructions = "scope"\n'
        'model = "unsupported-model"\nmodel_reasoning_effort = "medium"\n'
        'sandbox_mode = "workspace-write"',
    ],
)
def test_doctor_rejects_malformed_or_wrong_model_worker(
    tmp_path: Path, capsys, content: str
) -> None:
    apply_changes(tmp_path, plan_init(tmp_path))
    (tmp_path / ".codex/agents/gsp-worker.toml").write_text(content)
    assert cli.main(["doctor", str(tmp_path)]) == 1
    assert "FAIL agent TOML gsp-worker" in capsys.readouterr().out


@pytest.mark.parametrize("name", ["gsp-triage", "gsp-researcher", "gsp-reviewer"])
def test_doctor_rejects_writable_read_only_roles(tmp_path: Path, capsys, name: str) -> None:
    apply_changes(tmp_path, plan_init(tmp_path))
    path = tmp_path / f".codex/agents/{name}.toml"
    path.write_text(
        path.read_text().replace('sandbox_mode = "read-only"', 'sandbox_mode = "workspace-write"')
    )
    assert cli.main(["doctor", str(tmp_path)]) == 1
    assert f"FAIL agent TOML {name}" in capsys.readouterr().out


def test_installed_roles_match_local_contract_and_keep_main_settings(tmp_path: Path) -> None:
    config = tmp_path / ".codex/config.toml"
    config.parent.mkdir()
    original = b'model = "custom-main"\nmodel_reasoning_effort = "low"\n'
    config.write_bytes(original)
    apply_changes(tmp_path, plan_init(tmp_path))
    assert config.read_bytes() == original
    for name, (model, effort, sandbox) in AGENT_ROLES.items():
        agent = tomllib.loads((tmp_path / f".codex/agents/{name}.toml").read_text())
        assert agent["name"] == name
        assert agent["model"] == model
        assert agent["model_reasoning_effort"] == effort
        assert agent["sandbox_mode"] == sandbox
        assert "service_tier" not in agent
    for reference in ("parallel-work", "model-routing"):
        assert (tmp_path / SKILL_DIR / "references" / f"{reference}.md").is_file()


@pytest.mark.parametrize("command", ["init", "setup"])
def test_cli_defaults_to_180_and_adopts_installed_instructions(
    tmp_path: Path, capsys, command: str
):
    assert cli.main([command, str(tmp_path)]) == 0
    assert "180" in (tmp_path / "TASK.md").read_text()
    output = capsys.readouterr().out
    assert "설치한 AGENTS.md, TASK.md" in output
    assert "gsp prompt start" not in output


def test_doctor_accepts_supported_explicit_role_override(tmp_path: Path, capsys) -> None:
    apply_changes(tmp_path, plan_init(tmp_path))
    reviewer = tmp_path / AGENT_FILE
    reviewer.write_text(
        reviewer.read_text()
        .replace('model = "gpt-6.1-sol"', 'model = "gpt-6-luna"')
        .replace('model_reasoning_effort = "medium"', 'model_reasoning_effort = "high"')
    )
    assert cli.main(["doctor", str(tmp_path)]) == 0
    assert "PASS agent TOML gsp-reviewer: gpt-6-luna, high, read-only" in capsys.readouterr().out
