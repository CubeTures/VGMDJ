import os
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path
from time import sleep
from urllib.parse import urlparse

from uuid_utils import uuid7

from pykhinsider import Album
from src import FLARESOLVERR_URL, MUSIC_DIR, TMP_DIR
from src.auto_hide import refresh_auto_hidden_single
from src.jellyfin import JellyfinClient
from src.prefs import load_prefs
from src.status import DownloadFunc, DownloadRunner, Status
from src.utils import tag_folder


@dataclass
class DownloadInfo:
    game: str
    franchise: str
    url: str
    quality: str

    @property
    def album(self) -> str:
        path = urlparse(self.url).path
        return Path(path).name

    def franchise_folder(self) -> Path:
        return Path(MUSIC_DIR) / self.franchise

    def album_folder(self) -> Path:
        return self.franchise_folder() / self.game

    def tmp_franchise_folder(self) -> Path:
        return Path(TMP_DIR) / self.franchise

    def tmp_album_folder(self) -> Path:
        return self.tmp_franchise_folder() / self.album


def create_downloader(info: DownloadInfo):
    album = Album(
        f"https://downloads.khinsider.com/game-soundtracks/album/{info.album}"
    )
    func: DownloadFunc = lambda callback: album.download_all(
        info.quality,
        dest=str(info.tmp_franchise_folder()),
        flaresolverr_url=FLARESOLVERR_URL,
        progress_callback=callback,
    )
    downloader = DownloadRunner(str(uuid7()), asdict(info), func)
    return downloader


def _make_dirs(info: DownloadInfo):
    os.makedirs(info.tmp_album_folder(), exist_ok=True)
    os.makedirs(info.franchise_folder(), exist_ok=True)


def _tag_audio(info: DownloadInfo) -> None:
    tag_folder(info.game, info.franchise, info.tmp_album_folder())
    (info.tmp_album_folder() / "README.md").write_text(f"[Source]({info.url})")


def _apply_prefs(info: DownloadInfo):
    time = load_prefs().auto_hide_time
    refresh_auto_hidden_single(None, time, info.tmp_album_folder())


def _move_dir(info: DownloadInfo):
    shutil.move(info.tmp_album_folder(), info.album_folder())
    os.rmdir(info.tmp_franchise_folder())


def _wait_for_update(client: JellyfinClient, info: DownloadInfo):
    while True:
        sleep(1)
        if client.search_folder(info.game, info.franchise) is not None:
            return


def run_download(client: JellyfinClient, info: DownloadInfo):
    dl = create_downloader(info)
    dl.record_status(Status.STARTED)
    _make_dirs(info)
    dl.record_status(Status.INITIALIZED)
    dl.execute()
    dl.record_status(Status.DOWNLOADED)
    _tag_audio(info)
    dl.record_status(Status.TAGGED)
    _apply_prefs(info)
    dl.record_status(Status.CLEANED)
    _move_dir(info)
    dl.record_status(Status.MOVED)
    _wait_for_update(client, info)
    dl.record_status(Status.COMPLETED)
