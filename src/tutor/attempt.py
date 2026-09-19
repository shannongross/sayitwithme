import tempfile
from pathlib import Path

from tutor.stt import transcribe
from tutor.text import is_understood


extensions = {
    "audio/webm": "webm",
    "audio/mp4": "mp4",
    "audio/mpeg": "mp3",
}


async def assess(audio: bytes, content_type: str, phrase: dict) -> dict:
    suffix = extensions.get(content_type)
    if suffix is None:
        raise ValueError("unsupported audio type")

    with tempfile.TemporaryDirectory() as directory:
        audio_path = Path(directory) / f"attempt.{suffix}"
        audio_path.write_bytes(audio)
        transcript = await transcribe(audio_path)

    result = "understood" if is_understood(transcript, phrase) else "not_yet"
    return {"result": result}