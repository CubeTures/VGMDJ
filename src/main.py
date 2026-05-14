import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from src.utils import get_dir
from src.ignore import add_ignore, remove_ignore, read_ignore, unescape_ignore

MUSIC_EXTENSIONS = {".mp3", ".flac", ".wav", ".aac", ".ogg", ".m4a"}

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8000"],
    allow_methods=["*"],
)

STATIC_DIR = Path(__file__).parent.parent / "frontend" / "build"
app.mount("/web", StaticFiles(directory=STATIC_DIR, html=True), name="web")


@app.get("/health")
def health_check() -> str:
    return "healthy"


@app.post("/walk")
def folders(dirs: list[str] = []):
    base = get_dir(dirs)
    result: list[dict[str, str | bool]] = []
    ignored = read_ignore(base / ".ignore")
    ignored = unescape_ignore(ignored)

    for entry in os.scandir(base):
        if (
            not entry.is_dir()
            and Path(entry.name).suffix.lower() not in MUSIC_EXTENSIONS
        ):
            continue

        result.append(
            {
                "name": entry.name,
                "isDir": entry.is_dir(),
                "isHidden": entry.name in ignored,
            }
        )

    result.sort(key=lambda entry: entry["name"])
    return result


@app.post("/hide")
def hide(hidden: dict[str, bool], dirs: list[str] = []):
    base = get_dir(dirs)
    ignore = base / ".ignore"
    add = [f for (f, hide) in hidden.items() if hide]
    remove = [f for (f, hide) in hidden.items() if not hide]
    add_ignore(ignore, add)
    remove_ignore(ignore, remove)
