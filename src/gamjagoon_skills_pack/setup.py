"""Compose the complete project setup into one preflighted file transaction."""

from __future__ import annotations

from pathlib import Path

from .installer import Change, SetupError, plan_init, read_existing
from .keyboard import plan_keyboard


def plan_setup(
    root: Path, *, minutes: int = 180, overwrite: bool = False, keyboard: bool = True
) -> list[Change]:
    changes = plan_init(root, minutes=minutes, overwrite=overwrite)
    task, _ = read_existing(root, "TASK.md")
    if task == b"":
        raise SetupError(
            "기존 TASK.md가 비어 있습니다. 파일을 보존했으며 설치 전에 내용을 확인하세요."
        )
    if keyboard:
        changes.extend(plan_keyboard(root, overwrite=overwrite))
    merged: dict[str, Change] = {}
    for change in changes:
        previous = merged.get(change.relative)
        if previous is not None and previous != change:
            raise SetupError(
                f"설치 계획이 충돌합니다: {change.relative}; 파일을 변경하지 않았습니다."
            )
        merged[change.relative] = change
    return list(merged.values())
