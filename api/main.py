from contextlib import asynccontextmanager
from uuid import UUID

import asyncpg
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api import config
from api.attempt import assess
from api.content import find_phrase_text, list_categories, list_phrases


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = await asyncpg.create_pool(
        config.database_url, min_size=1, max_size=5
    )
    yield
    await app.state.pool.close()


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
app.mount(
    "/media", StaticFiles(directory=config.content_dir / "media"), name="media"
)


@app.get("/api/categories")
async def get_categories(request: Request) -> list[dict]:
    return await list_categories(request.app.state.pool)


@app.get("/api/categories/{category}")
async def get_phrases(request: Request, category: str) -> list[dict]:
    return await list_phrases(request.app.state.pool, category)


@app.post("/api/attempts")
async def create_attempt(
    request: Request,
    phrase_id: UUID = Form(),
    audio: UploadFile = File(),
) -> dict:
    text = await find_phrase_text(request.app.state.pool, phrase_id)
    if text is None:
        raise HTTPException(status_code=404, detail="unknown phrase")

    audio_bytes = await audio.read()
    if len(audio_bytes) > 1_000_000:
        raise HTTPException(status_code=413, detail="audio is too large")

    try:
        return await assess(audio_bytes, audio.content_type or "", text)
    except ValueError as error:
        raise HTTPException(status_code=415, detail=str(error)) from error
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
