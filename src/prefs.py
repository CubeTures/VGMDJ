import json
from dataclasses import asdict, dataclass
from pathlib import Path

from src import WORKING_DIR
from src.utils import lock_file

PREFS_FILE = Path(WORKING_DIR) / "prefs.json"


@dataclass
class Prefs:
    auto_hide_time: int = 0


def load_prefs():
    with lock_file(PREFS_FILE):
        if not PREFS_FILE.exists():
            return Prefs()
        with open(PREFS_FILE, "r") as file:
            return Prefs(**json.load(file))


def save_prefs(prefs: Prefs):
    with lock_file(PREFS_FILE):
        with open(PREFS_FILE, "w") as file:
            file.write(json.dumps(asdict(prefs)))
