# Say It With Me

One small phone-first demo for practicing an English phrase without reading.

The browser records an attempt, sends it to OpenAI transcription, compares the returned text to the target phrase, and deletes the temporary upload before responding. It stores no learner audio or transcript.

## Run locally

Install Python 3.11+, Node, and [uv](https://docs.astral.sh/uv/). Set `OPENAI_API_KEY` in your shell before starting the API.

```sh
uv sync
uv run uvicorn tutor.api.main:app --reload
```

In another terminal:

```sh
cd web
npm install
npm run dev
```

This first slice has one phrase and one direct transcription provider. It does not include first-language audio, accounts, saved recordings, an LLM tutor, or volunteer content.