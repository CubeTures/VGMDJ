from threading import Lock
from typing import Callable, Any
from enum import StrEnum, auto
from time import time, monotonic

from asyncio import Queue, AbstractEventLoop

type DownloadFunc = Callable[[Callable[[str], None] | None], None]

_loop: AbstractEventLoop
_subscribers: set[Queue[dict[str, Any]]] = set()
_mutex = Lock()
_latest_messages: dict[str, dict[str, Any]] = {}


def set_loop(loop: AbstractEventLoop):
    global _loop
    _loop = loop


def subscribe() -> Queue[dict[str, Any]]:
    queue: Queue[dict[str, Any]] = Queue()
    with _mutex:
        for message in _latest_messages.values():
            queue.put_nowait(message)
        _subscribers.add(queue)
    return queue


def unsubscribe(queue: Queue[dict[str, Any]]):
    _subscribers.discard(queue)


def _notify(payload: dict[str, Any]):
    with _mutex:
        if payload["id"] not in _latest_messages and len(_latest_messages.keys()) >= 10:
            id = min(_latest_messages, key=lambda id: _latest_messages[id]["timestamp"])
            del _latest_messages[id]
        _latest_messages[payload["id"]] = payload

    for queue in _subscribers:
        _loop.call_soon_threadsafe(queue.put_nowait, payload)


class Status(StrEnum):
    STARTED = auto()
    INITIALIZED = auto()
    PROGRESS = auto()
    DOWNLOADED = auto()
    TAGGED = auto()
    MOVED = auto()
    CLEANED = auto()
    COMPLETED = auto()


class _ProgressCallback:
    def __init__(self, notify: Callable[[dict[str, Any]], None]) -> None:
        self._notify = notify
        self._last_notify = 0.0

    def write(self, text: str):
        stripped = text.strip("\r\n ")
        if stripped:
            parsed = self._parse(stripped)
            now = monotonic()
            if now - self._last_notify >= 5.0:
                self._notify({"status": Status.PROGRESS, "progress": parsed})
                self._last_notify = now

    def _parse(self, text: str) -> dict[str, str]:
        filename, percent, size, speed, track = text.split(" | ")
        return {
            "filename": filename,
            "percent": percent.strip(),
            "size": size.strip(),
            "speed": speed.strip(),
            "track": track.strip(),
        }


class DownloadRunner:
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
        self._capture = _ProgressCallback(self._notify)

    def execute(self):
        self._func(self._capture.write)

    def record_status(self, status: Status):
        self._notify({"status": status})

    def _notify(self, payload: dict[str, Any]):
        _notify(
            {
                **payload,
                "id": self._id,
                "meta": self._meta,
                "timestamp": time() * 1000,
            }
        )
