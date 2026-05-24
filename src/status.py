import json
from typing import Callable, Any
from pathlib import Path
from enum import StrEnum, auto
from time import time

from src import WORKING_DIR
from src.utils import lock_file

type DownloadFunc = Callable[[Callable[[str], None] | None], None]


class Status(StrEnum):
    STARTED = auto()
    DOWNLOADED = auto()
    COMPLETED = auto()


class _ProgressCallback:
    def __init__(self) -> None:
        self.updates: list[dict[str, str]] = []

    def write(self, text: str):
        stripped = text.strip("\r\n ")
        if stripped:
            self.updates.append(self._parse(stripped))

    def _parse(self, text: str) -> dict[str, str]:
        filename, percent, size, speed = text.split(" | ")
        return {
            "filename": filename,
            "percent": percent.strip(),
            "size": size.strip(),
            "speed": speed.strip(),
        }


class DownloadRunner:
    _STATUS_JSON = Path(WORKING_DIR) / "status.json"
    _capture: _ProgressCallback

    def __init__(
        self,
        id: str,
        meta: dict[str, Any],
        func: DownloadFunc,
    ) -> None:
        self._id = id
        self._meta = meta
        self._func = func
        self._capture = _ProgressCallback()

    def execute(self):
        self.record_status(Status.STARTED)
        self._func(self._capture.write)
        self.record_status(Status.DOWNLOADED)

    @property
    def updates(self):
        return self._capture.updates

    def _load_status(self) -> dict[str, Any]:
        with lock_file(self._STATUS_JSON):
            if not self._STATUS_JSON.exists():
                return {}
            with open(self._STATUS_JSON, "r") as file:
                return json.load(file)

    def _save_status(self, data: dict[str, Any]):
        with lock_file(self._STATUS_JSON):
            with open(self._STATUS_JSON, "w") as file:
                file.write(json.dumps(data))

    def record_status(self, status: Status):
        with lock_file(self._STATUS_JSON):
            data = self._load_status()

            if self._id not in data and len(data.keys()) >= 10:
                id = min(data, key=lambda id: data[id]["timestamp"])
                del data[id]

            data[self._id] = {
                "meta": self._meta,
                "timestamp": time() * 1000,
                "status": status,
            }

            self._save_status(data)
