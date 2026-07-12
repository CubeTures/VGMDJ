import base64
from pathlib import Path

from fastapi import (
    HTTPException,
)
from mutagen.flac import FLAC, Picture
from mutagen.id3 import ID3
from mutagen.id3._frames import APIC
from mutagen.id3._util import ID3NoHeaderError
from mutagen.mp4 import MP4, MP4Cover
from mutagen.oggvorbis import OggVorbis

from src.utils import dirs_to_path

COVER_IMAGE_EXTENSIONS = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


def get_cover_image(dirs: list[str]) -> Path | None:
    base = dirs_to_path(dirs)
    stem: str = "folder" if len(dirs) == 1 else "cover"
    for ext in COVER_IMAGE_EXTENSIONS.values():
        path = base / f"{stem}{ext}"
        if path.exists():
            return path
    return None


def write_cover(base: Path, stem: str, content_type: str | None, data: bytes) -> str:
    ext = COVER_IMAGE_EXTENSIONS.get(content_type or "")
    if ext is None:
        raise HTTPException(400, "Unsupported image type")

    for existing in base.glob(f"{stem}.*"):
        existing.unlink()
    (base / f"{stem}{ext}").write_bytes(data)
    return content_type  # type: ignore


def embed_cover(path: Path, data: bytes, mime: str) -> None:
    suffix = path.suffix.lower()

    if suffix == ".flac":
        audio = FLAC(path)
        picture = Picture()
        picture.data = data
        picture.mime = mime
        picture.type = 3
        audio.clear_pictures()
        audio.add_picture(picture)
        audio.save()
    elif suffix == ".m4a":
        audio = MP4(path)
        fmt = MP4Cover.FORMAT_PNG if mime == "image/png" else MP4Cover.FORMAT_JPEG
        audio.tags["covr"] = [MP4Cover(data, imageformat=fmt)]  # type: ignore
        audio.save()
    elif suffix == ".ogg":
        audio = OggVorbis(path)
        picture = Picture()
        picture.data = data
        picture.mime = mime
        picture.type = 3
        audio["metadata_block_picture"] = [
            base64.b64encode(picture.write()).decode("ascii")
        ]
        audio.save()
    else:
        try:
            tags = ID3(path)
        except ID3NoHeaderError:
            tags = ID3()
        tags.delall("APIC")
        tags.add(APIC(encoding=3, mime=mime, type=3, desc="Cover", data=data))
        tags.save(path)
