"""The gsp CLI installs and prints workflow assets; it never invokes a model."""

from __future__ import annotations

import argparse
import shutil
import sys
import tomllib
from pathlib import Path

from . import __version__
from .installer import (
    AGENT_FILE,
    SKILL_DIR,
    SetupError,
    apply_changes,
    asset_root,
    plan_init,
    project_root,
    read_existing,
)

STAGES = (
    "start",
    "requirements",
    "requirements-review",
    "design-tasks",
    "plan-review",
    "feasibility",
    "implement",
    "implementation-review",
    "verify",
    "handoff",
)


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(
        prog="gsp", description="제한 시간 개발을 위한 Codex 워크플로·프롬프트 설치기"
    )
    root.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    commands = root.add_subparsers(dest="command", required=True)
    setup = commands.add_parser("setup", help="워크플로·리뷰어·줄바꿈을 한 번에 구성하고 검사")
    setup.add_argument("path", nargs="?", default=".")
    setup.add_argument("--minutes", type=int, default=180, help="실제 제작 시간 예산 (기본: 180분)")
    setup.add_argument(
        "--dry-run", action="store_true", help="모든 충돌을 확인하고 변경 계획만 출력"
    )
    setup.add_argument("--overwrite", action="store_true", help="관리 파일 충돌을 백업 후 교체")
    setup.add_argument("--no-keyboard", action="store_true", help="기존 Enter 동작을 유지")
    init = commands.add_parser("init", help="새 폴더 또는 기존 프로젝트에 워크플로 설치")
    init.add_argument("path", nargs="?", default=".")
    init.add_argument("--minutes", type=int, default=240, help="실제 제작 시간 예산 (기본: 240분)")
    init.add_argument("--dry-run", action="store_true", help="파일과 폴더를 만들지 않고 계획 출력")
    init.add_argument("--overwrite", action="store_true", help="충돌하는 관리 파일을 백업 후 교체")
    prompt = commands.add_parser("prompt", help="단계별 한국어 프롬프트 출력 (모델 호출 없음)")
    prompt.add_argument("stage", nargs="?", choices=STAGES)
    doctor = commands.add_parser("doctor", help="설치 파일·TOML·도구 존재의 로컬 정적 검사")
    doctor.add_argument("path", nargs="?", default=".")
    keyboard = commands.add_parser("keyboard", help="Codex CLI 프로젝트 로컬 줄바꿈·전송 키 설정")
    keyboard.add_argument("path", nargs="?", default=".")
    keyboard.add_argument("--enter", choices=("newline", "submit"), default="newline")
    keyboard.add_argument("--dry-run", action="store_true", help="파일 변경 없이 입력 키 계획 출력")
    skills = commands.add_parser("skills", help="선택 외부 스킬 카탈로그 및 명시적 다운로드")
    skill_commands = skills.add_subparsers(dest="skill_command", required=True)
    skill_commands.add_parser("list", help="출처·고정 커밋·라이선스 목록 출력")
    add = skill_commands.add_parser("add", help="선택한 외부 스킬 전체 폴더를 다운로드")
    add.add_argument("name")
    add.add_argument("--path", default=".")
    add.add_argument("--dry-run", action="store_true", help="다운로드·파일 작성 없이 출처 표시")
    return root


def doctor(path: str) -> int:
    root = project_root(path)
    errors = 0
    expected = ["AGENTS.md", "TASK.md", AGENT_FILE, f"{SKILL_DIR}/SKILL.md"]
    expected.extend(f"{SKILL_DIR}/references/{stage}.md" for stage in STAGES)
    for relative in expected:
        content, _ = read_existing(root, relative)
        if content:
            print(f"PASS file {relative}")
        else:
            errors += 1
            print(f"FAIL missing/empty {relative}")
    instructions, _ = read_existing(root, "AGENTS.md")
    if instructions and b"GAMJAGOON-SKILLS-PACK:START" not in instructions:
        errors += 1
        print("FAIL AGENTS.md에 워크플로 관리 블록이 없습니다.")
    agent_bytes, _ = read_existing(root, AGENT_FILE)
    if agent_bytes:
        try:
            agent = tomllib.loads(agent_bytes.decode("utf-8"))
            required = ("name", "description", "developer_instructions")
            if any(not isinstance(agent.get(key), str) or not agent[key] for key in required):
                raise ValueError("필수 에이전트 필드가 없습니다.")
            if agent.get("sandbox_mode") != "read-only":
                raise ValueError("리뷰어가 read-only가 아닙니다.")
            if any(key in agent for key in ("model", "model_reasoning_effort", "service_tier")):
                raise ValueError("리뷰어가 모델·추론·속도 설정을 지정하고 있습니다.")
            print("PASS reviewer TOML: read-only, 모델·추론 설정 미지정")
        except (ValueError, UnicodeError) as exc:
            errors += 1
            print(f"FAIL reviewer TOML: {exc}")
    for name in ("uv", "codex", "git"):
        status = "PASS" if shutil.which(name) else "WARN"
        print(f"{status} command {name} (존재만 확인)")
    if (root / "AGENTS.override.md").exists():
        print("WARN AGENTS.override.md가 있어 같은 경로의 AGENTS.md를 가릴 수 있습니다.")
    print("NOT_RUN 실제 Codex 지침 탐색·서브에이전트 실행·시험환경 동작")
    return 1 if errors else 0


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "setup":
            from .setup import plan_setup

            root = project_root(args.path)
            changes = plan_setup(
                root,
                minutes=args.minutes,
                overwrite=args.overwrite,
                keyboard=not args.no_keyboard,
            )
            for change in changes:
                print(f"{change.action} {change.relative}")
            if args.dry_run:
                print(f"DRY_RUN {len(changes)} files; 파일·폴더 변경 없음")
                return 0
            backups = apply_changes(root, changes)
            if backups:
                print(f"BACKUP {root / Path(backups[0]).parent}")
            status = doctor(str(root))
            if status:
                return status
            print(f"SETUP {len(changes)} changed files in {root}; 설치 파일 검사 완료")
            if not args.no_keyboard:
                print("KEYS Enter=줄바꿈; Alt+Enter=전송 (지원 시 Ctrl+Enter도 가능)")
                print("입력 키는 다음 Codex CLI 실행부터 확인하세요.")
            print(
                "설치한 AGENTS.md, TASK.md, .agents/skills/timeboxed-workflow/SKILL.md를 "
                "읽고 현재 대화에서 적용하세요. 과제 원문이 없으면 설치 완료 상태에서 기다리세요."
            )
        elif args.command == "init":
            root = project_root(args.path)
            changes = plan_init(root, minutes=args.minutes, overwrite=args.overwrite)
            for change in changes:
                print(f"{change.action} {change.relative}")
            if args.dry_run:
                print(f"DRY_RUN {len(changes)} files; 파일·폴더 변경 없음")
            else:
                backups = apply_changes(root, changes)
                print(f"INSTALLED {len(changes)} changed files in {root}")
                if backups:
                    print(f"BACKUP {root / Path(backups[0]).parent}")
                print("다음: gsp prompt start → Codex에 전달. 설치는 모델을 실행하지 않습니다.")
        elif args.command == "prompt":
            if args.stage is None:
                print("\n".join(STAGES))
            else:
                text = (
                    asset_root()
                    .joinpath("workflow", "references", f"{args.stage}.md")
                    .read_text(encoding="utf-8")
                )
                print(text, end="" if text.endswith("\n") else "\n")
        elif args.command == "doctor":
            return doctor(args.path)
        elif args.command == "keyboard":
            from .keyboard import plan_keyboard

            root = project_root(args.path)
            changes = plan_keyboard(root, enter=args.enter)
            if args.enter == "newline":
                print("KEYS Enter/Ctrl+J=줄바꿈; Alt+Enter=전송 (지원 시 Ctrl+Enter도 가능)")
            else:
                print("KEYS Enter=전송; Ctrl+J 또는 Shift+Enter/Alt+Enter=줄바꿈")
            for change in changes:
                print(f"{change.action} {change.relative}")
            if args.dry_run:
                print("DRY_RUN 파일·폴더 변경 없음")
            else:
                backups = apply_changes(root, changes)
                print(f"CONFIGURED {len(changes)} changed files in {root}")
                if backups:
                    print(f"BACKUP {root / Path(backups[0]).parent}")
                print("Codex CLI를 다시 실행해 입력을 확인하세요. 실제 터미널 전달은 환경별입니다.")
        else:
            from .external import add_skill, catalog

            if args.skill_command == "list":
                for item in catalog():
                    print(f"{item['name']} | {item['repository']}@{item['commit']}")
                    print(f"  {item['description']} | {item['license']}")
                    print(f"  {item['license_url']}")
                    if item.get("note"):
                        print(f"  NOTE {item['note']}")
            else:
                add_skill(args.name, project_root(args.path), dry_run=args.dry_run)
    except (SetupError, OSError, UnicodeError) as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
