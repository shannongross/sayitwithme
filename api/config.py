import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# The only place that knows how deep the package sits.
content_dir = Path(__file__).parents[1] / "content"

database_url = os.environ.get("DATABASE_URL", "")
cors_origins = os.environ.get("CORS_ORIGINS", "http://localhost:5173").split(",")
stt_model = os.environ.get("STT_MODEL", "gpt-4o-mini-transcribe")
openai_api_key = os.environ.get("OPENAI_API_KEY", "")
