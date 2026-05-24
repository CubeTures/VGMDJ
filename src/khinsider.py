import os
from pathlib import Path
from urllib.parse import urlparse
from dataclasses import dataclass, asdict
from uuid import uuid4

from pykhinsider import Album
from src import MUSIC_DIR, WORKING_DIR, FLARESOLVERR_URL
from src.utils import tag_folder
from src.status import DownloadRunner, DownloadFunc, Status
from src.jellyfin import JellyfinClient
from src.auto_hide import refresh_auto_hidden_single
from src.prefs import load_prefs

active_downloads: list[DownloadRunner] = []


@dataclass
class DownloadInfo:
    game: str
    franchise: str
    album: str
    quality: str

    def set_album_from_url(self, url: str):
        path = urlparse(url).path
        self.album = Path(path).name

    def franchise_folder(self) -> Path:
        return Path(MUSIC_DIR) / self.franchise

    def album_folder(self) -> Path:
        return self.franchise_folder() / self.game

    def tmp_franchise_folder(self) -> Path:
        return Path(WORKING_DIR) / "tmp" / self.franchise

    def tmp_album_folder(self) -> Path:
        return self.tmp_franchise_folder() / self.album


def _make_dirs(info: DownloadInfo):
    os.makedirs(info.tmp_album_folder(), exist_ok=True)
    os.makedirs(info.album_folder(), exist_ok=True)


def _download_album(info: DownloadInfo):
    album = Album(
        f"https://downloads.khinsider.com/game-soundtracks/album/{info.album}"
    )
    func: DownloadFunc = lambda callback: album.download_all(
        info.quality,
        dest=str(info.tmp_franchise_folder()),
        flaresolverr_url=FLARESOLVERR_URL,
        progress_callback=callback,
    )
    downloader = DownloadRunner(str(uuid4()), asdict(info), func)
    active_downloads.append(downloader)
    downloader.execute()
    return downloader


def _tag_audio(info: DownloadInfo) -> None:
    tag_folder(info.game, info.franchise, info.tmp_album_folder())


def _rename_dir(info: DownloadInfo):
    os.rename(info.tmp_album_folder(), info.album_folder())


def _cleanup_dirs(info: DownloadInfo):
    path = info.tmp_franchise_folder()
    os.rmdir(path)
    os.rmdir(path.parent)


def _initialize_dir(client: JellyfinClient, info: DownloadInfo):
    time = load_prefs().auto_hide_time
    refresh_auto_hidden_single(client, time, info.album_folder())


def run_download(client: JellyfinClient, info: DownloadInfo):
    _make_dirs(info)
    dl = _download_album(info)
    _tag_audio(info)
    _rename_dir(info)
    _cleanup_dirs(info)
    _initialize_dir(client, info)
    dl.record_status(Status.COMPLETED)
