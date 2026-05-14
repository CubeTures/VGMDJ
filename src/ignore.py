from pathlib import Path
import re


def escape_ignore(entry: str) -> str:
    return re.sub(r"([^\w.])", r"\\\1", entry)


def unescape_ignore(ignore: set[str]) -> set[str]:
    result: set[str] = set()
    for entry in ignore:
        result.add(re.sub(r"\\([^\w.])", r"\1", entry))
    return result


def read_ignore(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return set(path.read_text().splitlines())


def write_ignore(path: Path, entries: set[str]):
    if not entries:
        path.unlink(missing_ok=True)
        return
    path.write_text("\n".join(sorted(entries)))


def add_ignore(path: Path, entry: list[str]):
    entries = read_ignore(path)
    entries = entries.union(escape_ignore(e) for e in entry)
    write_ignore(path, entries)


def remove_ignore(path: Path, entry: list[str]):
    entries = read_ignore(path)
    entries = entries.difference(escape_ignore(e) for e in entry)
    write_ignore(path, entries)
