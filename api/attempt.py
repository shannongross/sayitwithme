import tempfile
from pathlib import Path

from api.stt import transcribe
from api.text import is_understood

extensions = {"audio/webm": "webm", "audio/mp4": "mp4"}


async def assess(audio: bytes, content_type: str, text: str) -> dict:
    media_type = content_type.split(";", 1)[0].lower()
    suffix = extensions.get(media_type)
    if suffix is None:
        raise ValueError("unsupported audio type")

    with tempfile.TemporaryDirectory() as directory:
        audio_path = Path(directory) / f"attempt.{suffix}"
        audio_path.write_bytes(audio)
        transcript = await transcribe(audio_path)

    result = "understood" if is_understood(transcript, text) else "not_yet"
    return {"result": result}
