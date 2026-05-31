from pathlib import Path
from typing import cast

from mutagen._file import File, FileType  # type: ignore

from src import MUSIC_DIR
from src.ignore import read_ignore, write_ignore
from src.jellyfin import JellyfinClient
from src.utils import is_song, path_to_dirs, refresh_dir_or_fallback


def _song_duration(path: Path) -> float | None:
    audio = cast(FileType | None, File(path, easy=True))
    return audio.info.length if (audio and audio.info) else None


def refresh_auto_hidden_single(client: JellyfinClient | None, time: int, folder: Path):
    ignore_file = Path(folder / ".ignore")
    entries = read_ignore(ignore_file)

    for song in folder.iterdir():
        if not is_song(song):
            continue
        duration = _song_duration(song)
        if duration is None:
            continue

        name = song.name
        is_under = duration < time
        is_auto = entries.get(name, {}).get("auto", False)
        if is_under and name not in entries:
            entries[name] = {"auto": True}
        elif not is_under and is_auto:
            entries.pop(name)

    write_ignore(ignore_file, entries)
    if client is not None:
        refresh_dir_or_fallback(client, path_to_dirs(folder))


def refresh_auto_hidden(client: JellyfinClient, time: int):
    base_dir = Path(MUSIC_DIR)
    folders = (
        p
        for p in base_dir.rglob("*")
        if p.is_dir() and not any(c.is_dir() for c in p.iterdir())
    )
    for folder in folders:
        refresh_auto_hidden_single(client, time, folder)
