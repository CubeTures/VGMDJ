import os
from functools import reduce
from pathlib import Path
from typing import cast

from fastapi import HTTPException
from filelock import FileLock
from mutagen._file import File, FileType  # type: ignore

from src import MUSIC_DIR
from src.constants import MUSIC_EXTENSIONS
from src.jellyfin import JellyfinClient


def tag_folder(album: str, album_artist: str, path: Path):
    field_map: dict[str, str] = {
        "ALBUM": album,
        "ALBUMARTIST": album_artist,
    }

    for file in os.listdir(path):
        file_path = path / file
        tags = cast(FileType | None, File(file_path, easy=True))

        if tags is None:
            continue

        for key, value in field_map.items():
            if value:
                tags[key] = value

        tags.save()  # type: ignore


def check_segment(name: str) -> str:
    """Reject anything that isn't a single plain path component (no traversal)."""
    if (
        name in ("", ".", "..")
        or os.sep in name
        or (os.altsep and os.altsep in name)
        or "\0" in name
    ):
        raise HTTPException(400, f"Invalid path segment: {name!r}")
    return name


def dirs_to_path(dirs: list[str]) -> Path:
    return reduce(lambda acc, f: acc / check_segment(f), dirs, Path(MUSIC_DIR))


def path_to_dirs(path: Path) -> list[str]:
    return list(path.relative_to(MUSIC_DIR).parts)


def is_song(path: Path) -> bool:
    return path.is_file and path.suffix in MUSIC_EXTENSIONS


def refresh_dir_or_fallback(
    client: JellyfinClient,
    dirs: list[str],
    image_refresh_mode: str | None = None,
):
    if len(dirs) > 1:
        folder = client.search_folder(dirs[-1], dirs[-2])
        if folder:
            client.refresh(folder, image_refresh_mode=image_refresh_mode)
        else:
            client.refresh_full()
    else:
        client.refresh_full()


def lock_file(path: Path) -> FileLock:
    return FileLock(path.with_suffix(path.suffix + ".lock"), is_singleton=True)
