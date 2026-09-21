import base64
from pathlib import Path

import httpx

from api import config

media_types = {".webm": "audio/webm", ".mp4": "audio/mp4"}

instruction = (
    "Transcribe the speech in this audio verbatim, in English. "
    "Return only the spoken words, with no commentary. "
    "If there is no speech, return nothing."
)


async def transcribe(audio_path: Path) -> str:
    if not config.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is required")

    audio = {
        "mime_type": media_types[audio_path.suffix],
        "data": base64.b64encode(audio_path.read_bytes()).decode(),
    }
    body = {
        "contents": [{"parts": [{"inline_data": audio}, {"text": instruction}]}],
        "generationConfig": {"temperature": 0},
    }
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{config.stt_model}:generateContent",
            json=body,
            headers={"x-goog-api-key": config.gemini_api_key},
        )
    response.raise_for_status()

    # Silence comes back with no parts rather than an empty string.
    parts = response.json()["candidates"][0]["content"].get("parts", [])
    return "".join(part.get("text", "") for part in parts)
