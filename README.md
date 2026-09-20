# Say It With Me

Practice saying English phrases out loud, without needing to read anything.

I built this for a Rohingya family who were resettled near me. The adults had never been to
school and do not read in any language, including their own, which is mostly a spoken one.
They wanted to learn enough English to get through a clinic visit or a bus ride on their own.
Every app I tried with them assumed you could read, if not English then at least the menus in
your first language. None of them worked for people who can't read at all.

So this one has no words on the screen. You tap a picture, hear the phrase, say it back, and
get a green check or an amber "try again". That's the whole app.

A few things follow from who it's for:

- It grades for being understood, not for sounding right. If you say "I need interpreter" you
  pass, because a nurse would understand you.
- It never says you failed. There are no scores, no streaks, and a bad network looks the same
  as "try again".
- Your voice is not kept. Recordings are transcribed and deleted in the same request.
- The Rohingya audio, when it exists, will come from Rohingya speakers. It will not be
  generated.

The pictures are from an AAC symbol library, the kind used by people who communicate without
text, because those are drawn to be understood on their own. Matching a phrase to a symbol
only on an exact label lost me pictures for about twenty phrases, but a wrong picture is worse
than none when the picture is the only thing carrying the meaning.

## Status

The learner flow works end to end with about a hundred words and short phrases. Not done yet:
deployment, the screen where volunteers record phrases in their own language, and any
measurement of how often the grader wrongly rejects someone who would have been understood.
That last one matters most, and I don't yet know the number.


## Run it

Needs Python 3.11+, Node, [uv](https://docs.astral.sh/uv/), and a Postgres database.

```sh
cp .env.example .env        # fill in DATABASE_URL and OPENAI_API_KEY
uv sync
psql "$DATABASE_URL" -f migrations/001_initial.sql
uv run python -m scripts.seed
uv run uvicorn api.main:app --reload
cd web && npm install && npm run dev
```

`uv run pytest` runs anywhere; the tests that need a database skip without `DATABASE_URL`.

## Licensing

The code is MIT. The pictograms in `content/media/img` are CC BY-SA 4.0 from
[Global Symbols](https://globalsymbols.com); see
[content/media/ATTRIBUTION.md](content/media/ATTRIBUTION.md) before redistributing them.
