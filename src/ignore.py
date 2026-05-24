import json
import re
from pathlib import Path
from typing import Any


def _escape_ignore(entry: str) -> str:
    return re.sub(r"([^\w.])", r"\\\1", entry)


def _unescape_ignore(entry: str) -> str:
    return re.sub(r"\\([^\w.])", r"\1", entry)


def read_ignore(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    lines = path.read_text().splitlines()
    result: dict[str, dict[str, Any]] = {}
    for i in range(0, len(lines) - 1, 2):
        meta = json.loads(lines[i][len("#!meta ") :])
        result[_unescape_ignore(lines[i + 1])] = meta
    return result


def write_ignore(path: Path, entries: dict[str, dict[str, Any]]) -> None:
    if not entries:
        path.unlink(missing_ok=True)
        return
    lines: list[str] = []
    for filename in sorted(entries):
        lines.append(f"#!meta {json.dumps(entries[filename], separators=(',', ':'))}")
        lines.append(_escape_ignore(filename))
    path.write_text("\n".join(lines))


def add_ignore(
    path: Path, entries: list[str], meta: dict[str, Any] | None = None
) -> None:
    current = read_ignore(path)
    for e in entries:
        current[e] = meta or {}
    write_ignore(path, current)


def remove_ignore(path: Path, entries: list[str]) -> None:
    current = read_ignore(path)
    for e in entries:
        current.pop(e, None)
    write_ignore(path, current)
