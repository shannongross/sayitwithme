import pytest
from fastapi.testclient import TestClient

from api import attempt, config, main

pytestmark = pytest.mark.skipif(
    not config.database_url, reason="DATABASE_URL is not set"
)


@pytest.fixture
def client():
    with TestClient(main.app) as started:
        yield started


@pytest.fixture
def phrase(client):
    categories = client.get("/api/categories").json()
    assert categories, "no content in the database; run scripts/seed.py"
    return client.get(f"/api/categories/{categories[0]['id']}").json()[0]


def test_a_category_serves_phrases_with_pictures(phrase) -> None:
    assert phrase["text"]
    assert phrase["image_url"].startswith("/media/img/")


def test_saying_the_phrase_is_understood(client, monkeypatch, phrase) -> None:
    monkeypatch.setattr(attempt, "transcribe", said(phrase["text"]))

    assert attempt_result(client, phrase) == "understood"


def test_saying_something_else_is_not_yet(client, monkeypatch, phrase) -> None:
    monkeypatch.setattr(attempt, "transcribe", said("I would like a taxi please."))

    assert attempt_result(client, phrase) == "not_yet"


def said(transcript: str):
    async def transcribe(audio_path) -> str:
        return transcript

    return transcribe


def attempt_result(client, phrase) -> str:
    response = client.post(
        "/api/attempts",
        data={"phrase_id": phrase["id"]},
        files={"audio": ("attempt", b"audio", "audio/webm;codecs=opus")},
    )
    assert response.status_code == 200
    return response.json()["result"]
