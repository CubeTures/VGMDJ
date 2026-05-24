from dataclasses import dataclass, asdict
from src import WORKING_DIR
from pathlib import Path
import json

PREFS_FILE = Path(WORKING_DIR) / "prefs.json"


@dataclass
class Prefs:
    auto_hide_time: int = 0


def load_prefs():
    if not PREFS_FILE.exists():
        return Prefs()
    with open(PREFS_FILE, "r") as file:
        return Prefs(json.load(file))


def save_prefs(prefs: Prefs):
    with open(PREFS_FILE, "w") as file:
        file.write(json.dumps(asdict(prefs)))
