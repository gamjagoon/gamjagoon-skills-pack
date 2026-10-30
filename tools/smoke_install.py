"""Exercise packaged resources through an isolated uv tool installation."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def main() -> None:
    repository = Path(__file__).resolve().parents[1]
    wheels = list((repository / "dist").glob("gamjagoon_skills_pack-*.whl"))
    if len(wheels) != 1:
        raise SystemExit("Run uv build first; dist/ must contain exactly one matching wheel.")
    uv = shutil.which("uv")
    if uv is None:
        raise SystemExit("uv is required.")
    with tempfile.TemporaryDirectory(prefix="gsp-smoke-") as temporary:
        root = Path(temporary)
        env = os.environ | {
            "UV_TOOL_DIR": str(root / "tools"),
            "UV_TOOL_BIN_DIR": str(root / "bin"),
            "UV_CACHE_DIR": str(root / "cache"),
            "UV_PYTHON_DOWNLOADS": "never",
        }

        def run(*arguments: str) -> str:
            result = subprocess.run(
                arguments, env=env, text=True, capture_output=True, check=True, cwd=root
            )
            return result.stdout

        run(uv, "tool", "install", "--python", sys.executable, str(wheels[0]))
        executable = str(root / "bin" / ("gsp.exe" if os.name == "nt" else "gsp"))
        project = root / "project"
        run(executable, "init", str(project), "--dry-run")
        assert not project.exists(), "dry-run created the target"
        run(executable, "init", str(project), "--minutes", "180")
        run(executable, "keyboard", str(project), "--dry-run")
        assert not (project / ".codex/config.toml").exists()
        run(executable, "keyboard", str(project))
        assert (
            'submit = ["alt-enter", "ctrl-enter"]' in (project / ".codex/config.toml").read_text()
        )
        assert "180" in (project / "TASK.md").read_text()
        assert "NOT_RUN" in run(executable, "doctor", str(project))
        assert run(executable, "prompt", "start").strip()
        assert "frontend-design" in run(executable, "skills", "list")
        assert "0 changed files" in run(executable, "init", str(project))
        assert run(
            uv, "tool", "run", "--from", str(wheels[0]), "gsp", "prompt", "plan-review"
        ).strip()
    print("PASS isolated uv tool install, bundled resources, init, doctor, prompts, and uvx path")


if __name__ == "__main__":
    main()
