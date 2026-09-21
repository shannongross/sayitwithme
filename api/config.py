import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# The only place that knows where content lives.
content_dir = Path(__file__).parents[1] / "content"
phrases_csv = content_dir / "phrases.csv"
media_dir = content_dir / "media"
images_dir = media_dir / "img"
manifest = media_dir / "MANIFEST.csv"

database_url = os.environ.get("DATABASE_URL", "")
cors_origins = os.environ.get("CORS_ORIGINS", "http://localhost:5173").split(",")
stt_model = os.environ.get("STT_MODEL", "gemini-3.8-flash")
gemini_api_key = os.environ.get("GEMINI_API_KEY", "")
