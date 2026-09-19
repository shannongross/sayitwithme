from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from tutor.attempt import assess
from tutor.content import load_lesson


root = Path(__file__).parents[3]
lesson = load_lesson()
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
app.mount("/media", StaticFiles(directory=root / "content" / "media"), name="media")


@app.get("/api/lesson")
def get_lesson() -> dict:
    return lesson


@app.post("/api/attempts")
async def create_attempt(
    phrase_id: str,
    audio: UploadFile = File(),
) -> dict:
    if phrase_id != lesson["phrase"]["id"]:
        raise HTTPException(status_code=404, detail="unknown phrase")

    audio_bytes = await audio.read()
    if len(audio_bytes) > 1_000_000:
        raise HTTPException(status_code=413, detail="audio is too large")

    try:
        return await assess(audio_bytes, audio.content_type or "", lesson["phrase"])
    except ValueError as error:
        raise HTTPException(status_code=415, detail=str(error)) from error
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error