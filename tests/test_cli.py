import tomllib
from pathlib import Path

import pytest

from gamjagoon_skills_pack import cli
from gamjagoon_skills_pack.installer import AGENT_FILE, SKILL_DIR, apply_changes, plan_init


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


def test_installed_files_include_task_and_read_only_inherited_reviewer(tmp_path: Path) -> None:
    changes = plan_init(tmp_path, minutes=135)
    apply_changes(tmp_path, changes)
    task = (tmp_path / "TASK.md").read_text(encoding="utf-8")
    assert "135" in task
    reviewer = tomllib.loads((tmp_path / AGENT_FILE).read_text(encoding="utf-8"))
    assert reviewer["sandbox_mode"] == "read-only"
    assert not {"model", "model_reasoning_effort", "service_tier"} & reviewer.keys()


def test_doctor_reports_static_check_and_runtime_not_run(
    tmp_path: Path, capsys, monkeypatch
) -> None:
    apply_changes(tmp_path, plan_init(tmp_path))
    monkeypatch.setattr("shutil.which", lambda _name: None)
    assert cli.main(["doctor", str(tmp_path)]) == 0
    output = capsys.readouterr().out
    assert "PASS reviewer TOML" in output
    assert "NOT_RUN" in output
    assert "실제 Codex" in output
    assert "WARN command" in output


@pytest.mark.parametrize(
    "override", ["model = 'x'", "model_reasoning_effort = 'high'", "service_tier = 'priority'"]
)
def test_doctor_rejects_reviewer_runtime_overrides(tmp_path: Path, capsys, override: str) -> None:
    apply_changes(tmp_path, plan_init(tmp_path))
    reviewer = tmp_path / AGENT_FILE
    reviewer.write_text(reviewer.read_text(encoding="utf-8") + f"\n{override}\n", encoding="utf-8")
    assert cli.main(["doctor", str(tmp_path)]) == 1
    assert "FAIL reviewer TOML" in capsys.readouterr().out


def test_doctor_detects_missing_prompt_resource(tmp_path: Path, capsys) -> None:
    apply_changes(tmp_path, plan_init(tmp_path))
    (tmp_path / SKILL_DIR / "references/verify.md").unlink()
    assert cli.main(["doctor", str(tmp_path)]) == 1
    assert "FAIL missing/empty" in capsys.readouterr().out


def test_prompt_rejects_unknown_stage() -> None:
    with pytest.raises(SystemExit) as error:
        cli.main(["prompt", "unknown"])
    assert error.value.code == 2
