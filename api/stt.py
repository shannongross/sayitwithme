from pathlib import Path

import httpx

from api import config


async def transcribe(audio_path: Path) -> str:
    if not config.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is required")

    with audio_path.open("rb") as audio_file:
        files = {"file": (audio_path.name, audio_file, "application/octet-stream")}
        data = {"model": config.stt_model}
        headers = {"Authorization": f"Bearer {config.openai_api_key}"}
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                "https://api.openai.com/v1/audio/transcriptions",
                files=files,
                data=data,
                headers=headers,
            )
    response.raise_for_status()
    return response.json()["text"]
