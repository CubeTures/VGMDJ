import os
from dotenv import load_dotenv

load_dotenv()

MUSIC_DIR = os.environ["MUSIC_DIR"]
JELLYFIN_URL = os.environ["JELLYFIN_URL"]
JELLYFIN_USER_ID = os.environ["JELLYFIN_USER_ID"]
JELLYFIN_TOKEN = os.environ["JELLYFIN_TOKEN"]
