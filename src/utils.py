import os
from functools import reduce
from pathlib import Path
from typing import cast

from mutagen._file import File, FileType  # type: ignore
from filelock import FileLock

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


def dirs_to_path(dirs: list[str]) -> Path:
    return reduce(lambda acc, f: acc / f, dirs, Path(MUSIC_DIR))


def path_to_dirs(path: Path) -> list[str]:
    return list(path.relative_to(MUSIC_DIR).parts)


def is_song(path: Path) -> bool:
    return path.is_file and path.suffix in MUSIC_EXTENSIONS


def refresh_dir_or_fallback(client: JellyfinClient, dirs: list[str]):
    if len(dirs) > 1:
        folder = client.search_folder(dirs[-1], dirs[-2])
        if folder:
            client.refresh(folder)
        else:
            client.refresh_full()
    else:
        client.refresh_full()


def lock_file(path: Path) -> FileLock:
    return FileLock(path.with_suffix(path.suffix + ".lock"), is_singleton=True)
