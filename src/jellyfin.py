import uuid
from enum import StrEnum
from pathlib import Path
from typing import Any, cast

import requests

from src import JELLYFIN_USER_ID


class MediaType(StrEnum):
    AUDIO = "Audio"
    MUSIC_ALBUM = "MusicAlbum"
    MUSIC_ARTIST = "MusicArtist"


class Song:
    id: uuid.UUID
    file_name: str
    album: str
    album_artist: str


class JellyfinClient:
    def __init__(self, base_url: str, api_key: str) -> None:
        self._base_url = base_url.rstrip("/")
        self._session = requests.Session()
        self._session.headers["Authorization"] = f"MediaBrowser Token={api_key}"

    def _get(self, path: str, params: dict[str, str] | None = None) -> dict[str, Any]:
        response = self._session.get(f"{self._base_url}{path}", params=params)
        response.raise_for_status()
        return response.json()

    def _post(self, path: str, params: dict[str, str] | None = None) -> None:
        response = self._session.post(f"{self._base_url}{path}", params=params)
        response.raise_for_status()

    def search(self, name: str, media_type: MediaType) -> dict[str, Any]:
        return self._get(
            "/Items",
            params={
                "SearchTerm": name,
                "IncludeItemTypes": media_type,
                "Recursive": "true",
            },
        )

    def search_folder(self, album: str, album_artist: str) -> uuid.UUID | None:
        data = self.search(album, MediaType.MUSIC_ALBUM)
        for item in data["Items"]:
            if "AlbumArtist" in item and item["AlbumArtist"] == album_artist:
                return uuid.UUID(item["Id"])
        return None

    def refresh(
        self,
        item_id: uuid.UUID,
        recursive: bool = True,
        image_refresh_mode: str | None = None,
    ) -> None:
        params = {"Recursive": str(recursive).lower()}
        if image_refresh_mode:
            params["ImageRefreshMode"] = image_refresh_mode
            params["MetadataRefreshMode"] = image_refresh_mode
        self._post(f"/Items/{item_id}/Refresh", params=params)

    def refresh_full(self) -> None:
        self._post("/Library/Refresh")

    def currently_playing(self) -> Song | None:
        sessions = cast(list[dict[str, Any]], self._get("/Sessions"))
        print(sessions)
        for session in sessions:
            if "UserId" in session and session["UserId"] == JELLYFIN_USER_ID:
                if "NowPlayingItem" in session:
                    item = session["NowPlayingItem"]
                    song = Song()
                    song.id = uuid.UUID(item["Id"])
                    song.file_name = str(Path(item["Path"]).name)
                    song.album = item["Album"]
                    song.album_artist = item["AlbumArtist"]
                    return song

        return None
