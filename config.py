import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

# Cargar variables de entorno
load_dotenv(BASE_DIR / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "").strip()
DEFAULT_COUNTRY = os.getenv("DEFAULT_COUNTRY", "ES").strip().upper()
LANGUAGE = os.getenv("LANGUAGE", "es-ES").strip()
DB_PATH = BASE_DIR / "watchlist.db"

