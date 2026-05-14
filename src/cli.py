from pykhinsider import Album
from utils import tag_folder

from urllib.parse import urlparse, unquote
from pathlib import Path
import argparse
import os
import csv
import shutil


class DownloadInfo:
    game: str
    franchise: str
    album: str
    quality: str


def download_album(info: DownloadInfo):
    album = Album(
        f"https://downloads.khinsider.com/game-soundtracks/album/{info.album}"
    )
    album.download_all(info.quality, dest="Music", use_flaresolverr=True)


def tag_audio(info: DownloadInfo) -> None:
    path = Path("Music") / info.album
    tag_folder(info.game, info.franchise, path)


def clean_titles(info: DownloadInfo):
    path = Path("Music") / info.album
    files = os.listdir(path)
    for file in files:
        po = path / file
        pc = path / unquote(file)
        os.rename(po, pc)


def rename_dir(info: DownloadInfo):
    path = Path("Music")
    orig = path / info.album
    new = path / info.game
    os.rename(orig, new)


def move_dir(info: DownloadInfo):
    path = Path("Music")
    parent = path / info.franchise
    os.makedirs(parent, exist_ok=True)

    orig = path / info.game
    new = parent / info.game
    shutil.move(orig, new)


def run(info: DownloadInfo):
    download_album(info)
    tag_audio(info)
    rename_dir(info)
    move_dir(info)


def parse_url(url: str):
    path = urlparse(url).path
    return Path(path).name


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "url",
        help="KHInsider album/song URL or direct download link",
    )
    parser.add_argument(
        "-n",
        "--name",
        help="The name of the game",
    )
    parser.add_argument(
        "-f",
        "--franchise",
        help="The franchise of the game",
    )
    parser.add_argument(
        "-q",
        "--quality",
        default="mp3",
        help="The quality of the music file",
    )
    parser.add_argument(
        "-i",
        "--ingest",
        help="Ingest the input csv file [format: name, franchise, url, quality (optional)]",
    )
    args = parser.parse_args()

    if args.ingest:
        with open(args.ingest) as ingest:
            reader = csv.reader(ingest)
            for row in reader:
                info = DownloadInfo()
                info.game = row[0]
                info.franchise = row[1]
                info.album = parse_url(row[2])
                info.quality = row[3] if len(row) > 3 else "mp3"
                run(info)
    else:
        info = DownloadInfo()
        info.game = args.name
        info.franchise = args.franchise
        info.album = parse_url(args.url)
        info.quality = args.quality
        run(info)


if __name__ == "__main__":
    main()
