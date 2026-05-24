import os
from pathlib import Path
from fastapi import FastAPI, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import Any
from src import JELLYFIN_URL, JELLYFIN_TOKEN
from src.utils import dirs_to_path, refresh_dir_or_fallback
from src.ignore import add_ignore, remove_ignore, read_ignore
from src.jellyfin import JellyfinClient
from src.metadata import read_metadata, get_hidden_count
from src.prefs import load_prefs, save_prefs
from src.constants import MUSIC_EXTENSIONS
from src.auto_hide import refresh_auto_hidden

client = JellyfinClient(JELLYFIN_URL, JELLYFIN_TOKEN)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8000"],
    allow_methods=["*"],
)


@app.get("/health")
def health_check() -> str:
    return "healthy"


@app.post("/walk")
def folders(dirs: list[str] = []):
    base = dirs_to_path(dirs)
    result: list[dict[str, Any]] = []
    ignored = read_ignore(base / ".ignore")

    for entry in os.scandir(base):
        if (
            not entry.is_dir()
            and Path(entry.name).suffix.lower() not in MUSIC_EXTENSIONS
        ):
            continue

        path = Path(entry.path)
        metadata = read_metadata(path) if not entry.is_dir() else get_hidden_count(path)
        result.append(
            {
                "name": entry.name,
                "isDir": entry.is_dir(),
                "isHidden": entry.name in ignored,
                "metadata": metadata,
            }
        )

    result.sort(key=lambda entry: entry["name"])
    return result


@app.post("/hide")
def hide(hidden: dict[str, bool], dirs: list[str] = []):
    base = dirs_to_path(dirs)
    ignore = base / ".ignore"
    add = [f for (f, hide) in hidden.items() if hide]
    remove = [f for (f, hide) in hidden.items() if not hide]
    add_ignore(ignore, add)
    remove_ignore(ignore, remove)
    refresh_dir_or_fallback(client, dirs)


@app.post("/boo")
def boo():
    song = client.currently_playing()
    if song == None:
        raise HTTPException(409)
    print(song.file_name)
    hide({song.file_name: True}, [song.album_artist, song.album])


@app.get("/auto-hide")
def get_auto_hide():
    return load_prefs().auto_hide_time


@app.post("/auto-hide")
def set_auto_hide(time: int = Body(...)):
    prefs = load_prefs()
    prefs.auto_hide_time = time
    save_prefs(prefs)
    refresh_auto_hidden(client, prefs.auto_hide_time)


STATIC_DIR = Path(__file__).parent.parent / "frontend" / "build"
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
