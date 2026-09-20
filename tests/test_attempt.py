import asyncio

from api import attempt


def test_accepts_webm_content_type_with_codec_parameter(monkeypatch) -> None:
    async def fake_transcribe(audio_path) -> str:
        assert audio_path.suffix == ".webm"
        return "I need an interpreter."

    monkeypatch.setattr(attempt, "transcribe", fake_transcribe)

    result = asyncio.run(
        attempt.assess(b"audio", "audio/webm;codecs=opus", "I need an interpreter.")
    )

    assert result == {"result": "understood"}
