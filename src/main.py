import asyncio
import csv
import io
import json
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import (
    BackgroundTasks,
    Body,
    FastAPI,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src import JELLYFIN_TOKEN, JELLYFIN_URL
from src.auto_hide import refresh_auto_hidden
from src.constants import MUSIC_EXTENSIONS
from src.cover import embed_cover, get_cover_image, write_cover
from src.ignore import read_ignore, update_ignore
from src.jellyfin import JellyfinClient
from src.khinsider import DownloadInfo, run_download
from src.metadata import TrackMeta, get_hidden_count, read_metadata
from src.prefs import PREFS_FILE, load_prefs, save_prefs
from src.status import set_loop, subscribe, unsubscribe
from src.utils import dirs_to_path, lock_file, refresh_dir_or_fallback

_client = JellyfinClient(JELLYFIN_URL, JELLYFIN_TOKEN)


@asynccontextmanager
async def lifespan(_: FastAPI):
    set_loop(asyncio.get_running_loop())
    yield


app = FastAPI(lifespan=lifespan)

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

    def sort_key(entry: dict[str, Any]) -> tuple[float, float, str]:
        meta = entry["metadata"]
        if isinstance(meta, TrackMeta):
            disc = meta.disc_number or float("inf")
            track = meta.track_number or float("inf")
            title = meta.title or entry["name"]
            return (disc, track, title)
        return (float("inf"), float("inf"), entry["name"])

    result.sort(key=sort_key)
    return result


@app.post("/hide")
def hide(hidden: dict[str, bool], dirs: list[str] = []):
    base = dirs_to_path(dirs)
    ignore = base / ".ignore"
    add = [f for (f, hide) in hidden.items() if hide]
    remove = [f for (f, hide) in hidden.items() if not hide]
    if update_ignore(ignore, add, remove):
        refresh_dir_or_fallback(_client, dirs)


@app.post("/boo")
def boo():
    song = _client.currently_playing()
    if song == None:
        raise HTTPException(409)
    print(song.file_name)
    hide({song.file_name: True}, [song.album_artist, song.album])


@app.get("/auto-hide")
def get_auto_hide():
    return load_prefs().auto_hide_time


@app.post("/auto-hide")
def set_auto_hide(time: int = Body(...)):
    with lock_file(PREFS_FILE):
        prefs = load_prefs()
        prefs.auto_hide_time = time
        save_prefs(prefs)
    refresh_auto_hidden(_client, prefs.auto_hide_time)


class KHInsiderRequest(BaseModel):
    url: str
    album: str
    album_artist: str
    quality: str


@app.post("/download/khinsider")
def download_khinsider(
    req: KHInsiderRequest,
    background_tasks: BackgroundTasks,
):
    info = DownloadInfo(
        req.album,
        req.album_artist,
        req.url,
        req.quality,
    )
    background_tasks.add_task(run_download, _client, info)


@app.post("/download/csv")
async def download_csv(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    content: bytes = await file.read()
    decoded: str = content.decode("utf-8")
    reader = csv.reader(io.StringIO(decoded))
    rows: list[list[str]] = [row for row in reader]

    def download_all(rows: list[list[str]]) -> None:
        for row in rows:
            info = DownloadInfo(row[0], row[1], row[2], row[3])
            run_download(_client, info)

    background_tasks.add_task(download_all, rows)


@app.get("/download-status")
def download_status() -> StreamingResponse:
    async def stream():
        queue = subscribe()
        try:
            while True:
                payload = await queue.get()
                yield f"data: {json.dumps(payload)}\n\n"
        finally:
            unsubscribe(queue)

    return StreamingResponse(stream(), media_type="text/event-stream")


@app.get("/cover")
def get_cover(dirs: list[str] = Query(default=[])):
    path = get_cover_image(dirs)
    if path:
        return FileResponse(path)
    raise HTTPException(404)


@app.post("/cover/album_artist")
async def album_artist_cover(
    dirs: str = Form(...),
    image: UploadFile = File(...),
):
    dirs_list: list[str] = json.loads(dirs)
    base = dirs_to_path(dirs_list)
    data = await image.read()

    write_cover(base, "folder", image.content_type, data)
    refresh_dir_or_fallback(_client, dirs_list, image_refresh_mode="FullRefresh")


@app.post("/cover/album")
async def album_cover(
    dirs: str = Form(...),
    image: UploadFile = File(...),
    override_tracks: bool = Form(False),
):
    dirs_list: list[str] = json.loads(dirs)
    base = dirs_to_path(dirs_list)
    data = await image.read()

    mime = write_cover(base, "cover", image.content_type, data)

    if override_tracks:
        for entry in os.scandir(base):
            if (
                entry.is_dir()
                or Path(entry.name).suffix.lower() not in MUSIC_EXTENSIONS
            ):
                continue
            embed_cover(Path(entry.path), data, mime)

    refresh_dir_or_fallback(_client, dirs_list, image_refresh_mode="FullRefresh")


STATIC_DIR = Path(__file__).parent.parent / "frontend" / "build"
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
