import os
from dotenv import load_dotenv

load_dotenv()

MUSIC_DIR = os.environ["MUSIC_DIR"]
JELLYFIN_USER = os.environ["JELLYFIN_USER"]
JELLYFIN_PASS = os.environ["JELLYFIN_PASS"]
