"""Project-local Codex CLI input profiles, preserving all unrelated TOML values."""

from __future__ import annotations

import copy
import json
import re
import tomllib
from pathlib import Path

from .installer import (
    STATE_DIR,
    Change,
    SetupError,
    ensure_project_scope,
    managed_change,
    read_existing,
)

CONFIG_FILE = ".codex/config.toml"
PROFILES = {
    "newline": {
        "composer": {"submit": ["alt-enter", "ctrl-enter"]},
        "editor": {"insert_newline": ["enter", "ctrl-j", "shift-enter"]},
    },
    "submit": {
        "composer": {"submit": ["enter", "ctrl-m"]},
        "editor": {"insert_newline": ["ctrl-j", "shift-enter", "alt-enter"]},
    },
}


def _read_toml(text: str) -> dict:
    try:
        return tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        raise SetupError(
            f"Codex 프로젝트 설정을 해석할 수 없습니다; 파일을 보존합니다: {exc}"
        ) from exc


def _expected_setting(data: dict, table: tuple[str, ...], key: str, value: list[str]) -> dict:
    expected = copy.deepcopy(data)
    cursor = expected
    for part in table:
        if part not in cursor:
            cursor[part] = {}
        if not isinstance(cursor[part], dict):
            raise SetupError(f"설정이 table 형식이 아닙니다: {'.'.join(table)}")
        cursor = cursor[part]
    cursor[key] = value
    return expected


def _set_value(text: str, table: tuple[str, ...], key: str, value: list[str]) -> str:
    """Patch ordinary table syntax, then prove all other parsed values stayed identical."""
    expected = _expected_setting(_read_toml(text), table, key, value)
    separator = "\r\n" if "\r\n" in text else "\n"
    assignment = f"{key} = {json.dumps(value)}{separator}"
    expression = r"^\s*\[\s*" + r"\s*\.\s*".join(map(re.escape, table))
    header = re.compile(expression + r"\s*\]\s*(?:#.*)?$")
    any_header = re.compile(r"^\s*\[.*\]\s*(?:#.*)?$")
    lines = text.splitlines(keepends=True)
    start = next((index for index, line in enumerate(lines) if header.match(line.strip())), None)
    if start is None:
        padding = "" if not text else (separator if text.endswith("\n") else separator * 2)
        updated = text + padding + f"[{'.'.join(table)}]{separator}" + assignment
    else:
        stop = next(
            (
                index
                for index in range(start + 1, len(lines))
                if any_header.match(lines[index].strip())
            ),
            len(lines),
        )
        key_line = re.compile(r"^\s*" + re.escape(key) + r"\s*=")
        index = next(
            (index for index in range(start + 1, stop) if key_line.match(lines[index])), None
        )
        if index is None:
            if not lines[start].endswith("\n"):
                lines[start] += separator
            lines.insert(start + 1, assignment)
        else:
            end = None
            for candidate in range(index + 1, stop + 1):
                try:
                    parsed = tomllib.loads("".join(lines[index:candidate]))
                except tomllib.TOMLDecodeError:
                    continue
                if key in parsed:
                    end = candidate
                    break
            if end is None:
                raise SetupError("키 설정의 범위를 안전하게 확인할 수 없습니다; 파일을 보존합니다.")
            lines[index:end] = [assignment]
        updated = "".join(lines)
    try:
        matches = tomllib.loads(updated) == expected
    except tomllib.TOMLDecodeError:
        matches = False
    if not matches:
        raise SetupError(
            "기존 TOML 표기에서는 입력 키만 안전하게 수정할 수 없습니다. "
            "파일을 보존했습니다. docs/keyboard.ko.md의 수동 설정을 사용하세요."
        )
    return updated


def plan_keyboard(root: Path, *, enter: str = "newline", overwrite: bool = False) -> list[Change]:
    ensure_project_scope(root)
    if enter not in PROFILES:
        raise SetupError(f"알 수 없는 Enter 프로필입니다: {enter}")
    original, mode = read_existing(root, CONFIG_FILE)
    try:
        text = (original or b"").decode("utf-8")
    except UnicodeError as exc:
        raise SetupError("Codex 프로젝트 설정이 UTF-8이 아닙니다; 파일을 보존합니다.") from exc
    _read_toml(text)
    for context, values in PROFILES[enter].items():
        for key, value in values.items():
            text = _set_value(text, ("tui", "keymap", context), key, value)
    result = []
    updated = text.encode()
    if original != updated:
        result.append(Change(CONFIG_FILE, original, updated, mode))
    ignored = managed_change(
        root, ".gitignore", f"{STATE_DIR}/\n".encode(), comment="#", overwrite=overwrite
    )
    if ignored is not None:
        result.append(ignored)
    return result
