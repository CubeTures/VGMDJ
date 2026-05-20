from dataclasses import dataclass
from pathlib import Path
from mutagen._file import File, FileType  # type: ignore
from typing import cast, Any
import os
from src.ignore import read_ignore, unescape_ignore
from src.constants import MUSIC_EXTENSIONS


@dataclass(frozen=True)
class TrackMeta:
    path: Path
    title: str | None
    artist: str | None
    track_number: int | None
    disc_number: int | None
    length: float | None


def _first(tags: dict[str, str], *keys: str) -> str | None:
    for key in keys:
        value = tags.get(key)
        if value:
            return str(value[0]) if isinstance(value, list) else str(value)
    return None


def _parse_number(raw: str | None) -> int | None:
    if raw is None:
        return None
    try:
        return int(str(raw).split("/")[0])
    except ValueError:
        return None


def read_metadata(path: Path) -> TrackMeta:
    audio = cast(FileType | None, File(path, easy=True))

    if audio is None:
        return TrackMeta(
            path=path,
            title=None,
            artist=None,
            track_number=None,
            disc_number=None,
            length=None,
        )

    tags: dict[str, Any] = audio.tags or {}

    return TrackMeta(
        path=path,
        title=_first(tags, "title"),
        artist=_first(tags, "artist", "albumartist"),
        track_number=_parse_number(_first(tags, "tracknumber")),
        disc_number=_parse_number(_first(tags, "discnumber")),
        length=audio.info.length if audio.info else None,
    )


def get_hidden_count(path: Path) -> dict[str, str | int]:
    total = 0
    hidden = 0
    dir_count = 0

    ignored = read_ignore(path / ".ignore")
    ignored = unescape_ignore(ignored)

    for entry in os.scandir(path):
        if entry.is_dir():
            dir_count += 1
        if entry.is_dir() or Path(entry.name).suffix.lower() not in MUSIC_EXTENSIONS:
            continue

        total += 1
        if entry.name in ignored:
            hidden += 1

    if total == 0:
        return {"path": str(path), "total": dir_count, "visible": -1}
    return {
        "path": str(path),
        "total": total,
        "visible": total - hidden,
    }
