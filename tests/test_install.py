"""Installer regressions; all writes are confined to temporary fixture projects."""

import os
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ("adopt", "grilling", "requirements", "architecture", "tasks", "development")
PAYLOAD = (
    "AGENTS.md",
    ".codex/agents/gsp-reviewer.toml",
    *(f".agents/skills/gsp-{name}/SKILL.md" for name in SKILLS),
    ".agents/skills/gsp-tasks/scripts/task_dag.py",
    ".agents/skills/gsp-tasks/references/task-dag.md",
    ".agents/skills/gsp-development/references/parallel-work.md",
    ".agents/skills/gsp-development/references/session-work.md",
    ".agents/skills/gsp-development/references/change-management.md",
    ".agents/skills/gsp-development/references/session-control.md",
    ".agents/skills/gsp-development/scripts/session_control.py",
)
LEGACY = tuple(
    f".agents/skills/gsp-{name}-review/SKILL.md"
    for name in ("requirements", "architecture", "development")
)


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def snapshot(path, exclude_backups=False):
    result = {}
    for file in path.rglob("*"):
        rel = file.relative_to(path)
        if exclude_backups and rel.parts[0] == ".gsp-backups":
            continue
        if file.is_symlink():
            result[str(rel)] = ("symlink", os.readlink(file))
        elif file.is_file():
            result[str(rel)] = ("file", file.read_bytes(), file.stat().st_mode)
    return result


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="gsp-install-test-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.source = self.base / "source"
        self.target = self.base / "project"
        for rel in ("install.sh", *PAYLOAD):
            dest = self.source / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / rel, dest)

    def install(self, *args, expected=0, extra_env=None):
        env = dict(os.environ, TMPDIR=str(self.base))
        env.update(extra_env or {})
        result = subprocess.run(
            ["bash", str(self.source / "install.sh"), *args, str(self.target)],
            cwd=self.base, env=env, text=True, capture_output=True,
        )
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def test_fresh_preview_install_and_repeat(self):
        self.install("--dry-run")
        self.assertFalse(self.target.exists())
        self.install()
        self.assertEqual(set(snapshot(self.target)), set(PAYLOAD) | {".gitignore"})
        for rel in PAYLOAD[1:]:
            self.assertEqual((self.target / rel).read_bytes(), (self.source / rel).read_bytes())
        agents = (self.source / "AGENTS.md").read_text()
        block = agents[agents.index("<!-- GAMJAGOON-SKILLS-PACK:START -->"):]
        self.assertEqual((self.target / "AGENTS.md").read_text(), block)
        self.assertFalse((self.target / "spec").exists())
        self.assertFalse((self.target / ".gsp-work").exists())
        self.assertFalse((self.target / ".codegraph").exists())
        self.assertFalse(list(self.target.rglob("*.html")))
        before = snapshot(self.target)
        self.assertIn("Already installed", self.install().stdout)
        self.assertEqual(snapshot(self.target), before)

    def test_unrelated_source_files_are_not_installed(self):
        unrelated = (
            "README.md", "spec/tasks.md", "tests/extra.py", "preview.html",
            ".env", ".serena/project.yml", ".codegraph/index.db",
            ".gsp-work/sessions/source/work.md", ".codex/config.toml",
            ".codex/agents/unrelated.toml", ".agents/skills/unrelated/SKILL.md",
            ".agents/skills/gsp-adopt/notes.md",
            ".agents/skills/gsp-tasks/scripts/unrelated.py",
            ".agents/skills/gsp-development/references/private.txt",
        )
        for rel in unrelated:
            write(self.source / rel, f"Do not install {rel}\n")
        self.install("--dry-run")
        self.assertFalse(self.target.exists())
        self.install()
        self.assertEqual(set(snapshot(self.target)), set(PAYLOAD) | {".gitignore"})
        for rel in unrelated:
            self.assertFalse((self.target / rel).exists(), rel)

    def test_installed_dag_cli(self):
        self.install()
        before = snapshot(self.target)
        plan = self.base / "tasks.md"
        task = dict(id="T1", title="First task", deps=[], status="pending",
                    owner="worker-a", reads=[], writes=["src"], resources=[])
        data = dict(version=1, max_parallel=1, tasks=[task])

        def save():
            write(plan, "<!-- GSP-DAG:START -->\n```json\n" +
                  json.dumps(data) + "\n```\n<!-- GSP-DAG:END -->\n")

        def run(command, expected=0):
            script = self.target / ".agents/skills/gsp-tasks/scripts/task_dag.py"
            result = subprocess.run(
                [sys.executable, "-B", str(script), command, str(plan)],
                cwd=self.base, text=True, capture_output=True,
            )
            self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
            return result.stdout

        save()
        plan_before = plan.read_bytes()
        self.assertTrue(json.loads(run("validate"))["valid"])
        self.assertEqual(json.loads(run("route"))["dispatch"][0]["task"], "T1")
        self.assertIn("flowchart", run("render"))
        self.assertEqual(plan.read_bytes(), plan_before)
        task["deps"] = ["T1"]
        save()
        invalid = json.loads(run("route", expected=2))
        self.assertFalse(invalid["valid"])
        self.assertNotIn("dispatch", invalid)
        self.assertEqual(snapshot(self.target), before)

    def test_installed_v2_and_manual_coordination(self):
        self.install()
        work = self.target / ".gsp-work"
        self.assertFalse(work.exists())
        write(work / "sessions/session-a/work.md", "Owner: session-a\n")
        plan = self.target / "spec/tasks.md"
        task = dict(id="T1", title="Verified artifact", deps=[], status="done",
                    owner="session-a", reads=[], writes=[], resources=[],
                    evidence="fixture result", basis={"R1": 1}, hold="C1")
        data = dict(version=2, plan_revision=5, max_parallel=1, contracts={"R1": 1},
                    tasks=[task], acceptance=[dict(id="A1", contracts={"R1": 1}, tasks=["T1"])])

        def save():
            write(plan, "<!-- GSP-DAG:START -->\n```json\n" + json.dumps(data) +
                  "\n```\n<!-- GSP-DAG:END -->\n")

        control = self.target / ".agents/skills/gsp-development/scripts/session_control.py"
        dag = self.target / ".agents/skills/gsp-tasks/scripts/task_dag.py"

        def call(script, *args, expected=0):
            result = subprocess.run([sys.executable, str(script), *map(str, args)],
                                    cwd=self.target, capture_output=True, text=True)
            self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
            return json.loads(result.stdout)

        def session(*args, expected=0):
            return call(control, "--work-root", work, *args, expected=expected)

        save()
        self.assertFalse(call(dag, "check", plan, expected=1)["complete"])
        session("register", "--session", "session-a", "--thread", "thread-a",
                "--tasks", "T1", "--document", plan)
        session("publish", "--change", "C1", "--expected-revision", "5",
                "--tasks", "T1", "--reason", "Check current basis", "--document", plan)
        session("ack", "--session", "session-a", "--change", "C1", "--revision", "4",
                "--state", "held", "--evidence", "wrong revision", expected=2)
        for state in ("held", "applied"):
            session("ack", "--session", "session-a", "--change", "C1", "--revision", "5",
                    "--state", state, "--evidence", "fixture checked " + state)
        del task["hold"]
        data["plan_revision"] = 6
        save()
        self.assertTrue(call(dag, "check", plan)["complete"])
        session("check", "--document", plan, expected=1)
        session("resolve", "--change", "C1", "--expected-revision", "6",
                "--document", plan, "--evidence", "current acceptance verified")
        session("check", "--document", plan)
        for rel in PAYLOAD[1:]:
            self.assertEqual((self.target / rel).read_bytes(), (self.source / rel).read_bytes())
        self.assertFalse(list((self.target / ".agents").rglob("__pycache__")))
        self.assertFalse(list(self.target.rglob("*.html")))

    def test_legacy_and_unrelated_files_are_unmanaged(self):
        unrelated = (
            *LEGACY, ".agents/skills/timeboxed-workflow/SKILL.md",
            ".codex/agents/old-role.toml", ".codex/config.toml",
            ".gsp-work/sessions/peer/work.md", "spec/tasks.md", "existing.html",
        )
        for rel in unrelated:
            write(self.target / rel, f"Preserve {rel}\n")
        before = snapshot(self.target)
        self.install("--dry-run")
        self.assertEqual(snapshot(self.target), before)
        self.install()
        self.install("--overwrite")
        after = snapshot(self.target)
        for rel, content in before.items():
            self.assertEqual(after[rel], content)
        self.assertFalse((self.target / ".gsp-backups").exists())

    def test_managed_conflict_preview_backup_and_repeat(self):
        self.install()
        for name in ("development", "adopt"):
            with self.subTest(skill=name):
                rel = f".agents/skills/gsp-{name}/SKILL.md"
                write(self.target / rel, "User customization\n")
                before = snapshot(self.target)
                self.install("--dry-run", expected=1)
                self.install(expected=1)
                self.assertEqual(snapshot(self.target), before)
                self.install("--overwrite", "--dry-run")
                self.assertEqual(snapshot(self.target), before)
                self.install("--overwrite")
                backups = list((self.target / ".gsp-backups").glob(f"install.*/{rel}"))
                self.assertEqual(len(backups), 1)
                self.assertEqual(backups[0].read_text(), "User customization\n")
                self.assertEqual((self.target / rel).read_bytes(), (self.source / rel).read_bytes())
                before = snapshot(self.target)
                self.install()
                self.assertEqual(snapshot(self.target), before)

    def test_write_failure_rolls_back_current_managed_files(self):
        write(self.target / "AGENTS.md", "User instructions\n")
        write(self.target / ".gitignore", "user-ignore\n")
        write(self.target / LEGACY[0], "Unmanaged legacy skill\n")
        before = snapshot(self.target)
        wrapper = self.base / "bin/mv"
        write(wrapper, """#!/usr/bin/env bash
if [[ ${@: -1} = "$GSP_TEST_FAIL_DEST" && ${@: -2:1} = */.gsp-write.* ]]; then
    printf 'Injected replacement failure\n' >&2
    exit 74
fi
exec "$GSP_TEST_REAL_MV" "$@"
""")
        wrapper.chmod(0o755)
        result = self.install(expected=74, extra_env={
            "PATH": str(wrapper.parent) + os.pathsep + os.environ["PATH"],
            "GSP_TEST_REAL_MV": shutil.which("mv"),
            "GSP_TEST_FAIL_DEST": str(self.target / ".codex/agents/gsp-reviewer.toml"),
        })
        self.assertIn("attempting rollback", result.stderr)
        self.assertEqual(snapshot(self.target, exclude_backups=True), before)
        backups = list((self.target / ".gsp-backups").glob("install.*/AGENTS.md"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), "User instructions\n")
        self.assertFalse(list(self.target.rglob(".gsp-write.*")))


if __name__ == "__main__":
    unittest.main()
