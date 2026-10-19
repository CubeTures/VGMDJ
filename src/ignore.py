import json
import os
import re
from pathlib import Path
from typing import Any

from filelock import FileLock

from src import WORKING_DIR
from src.utils import lock_file


def ignore_lock() -> FileLock:
    return lock_file(Path(WORKING_DIR) / "ignore")


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
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text("\n".join(lines))
    os.replace(tmp, path)


def update_ignore(
    path: Path,
    add: list[str],
    remove: list[str],
    meta: dict[str, Any] | None = None,
) -> bool:
    with ignore_lock():
        current = read_ignore(path)
        updated = dict(current)
        for e in add:
            updated[e] = meta or {}
        for e in remove:
            updated.pop(e, None)
        if updated == current:
            return False
        write_ignore(path, updated)
        return True
