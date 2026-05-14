import mutagen
from pathlib import Path
import os
from functools import reduce
from src import MUSIC_DIR


def tag_folder(album: str, album_artist: str, path: Path):
    field_map: dict[str, str] = {
        "ALBUM": album,
        "ALBUMARTIST": album_artist,
    }

    for file in os.listdir(path):
        file_path = path / file
        tags = mutagen.File(file_path, easy=True)

        if tags is None:
            continue

        for key, value in field_map.items():
            if value:
                tags[key] = value

        tags.save()


def get_dir(dirs: list[str]) -> Path:
    return reduce(lambda acc, f: acc / f, dirs, Path(MUSIC_DIR))
