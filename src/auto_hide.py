from pathlib import Path
from mutagen._file import File, FileType  # type: ignore
from typing import cast
from src.ignore import read_ignore, write_ignore
from src import MUSIC_DIR
from src.utils import is_song, path_to_dirs, refresh_dir_or_fallback
from src.jellyfin import JellyfinClient


def _song_duration(path: Path) -> float | None:
    audio = cast(FileType | None, File(path, easy=True))
    return audio.info.length if (audio and audio.info) else None


def refresh_auto_hidden(client: JellyfinClient, time: int) -> None:
    base_dir = Path(MUSIC_DIR)
    folders = (
        p
        for p in base_dir.rglob("*")
        if p.is_dir() and not any(c.is_dir() for c in p.iterdir())
    )

    for folder in folders:
        ignore_file = Path(folder / ".ignore")
        entries = read_ignore(ignore_file)

        for song in folder.iterdir():
            if not is_song(song):
                continue
            duration = _song_duration(song)
            if duration is None:
                continue

            name = song.name
            is_over = duration < time
            is_auto = entries.get(name, {}).get("auto", False)
            if is_over and name not in entries:
                entries[name] = {"auto": True}
            elif not is_over and is_auto:
                entries.pop(name)

        write_ignore(ignore_file, entries)
        refresh_dir_or_fallback(client, path_to_dirs(folder))
