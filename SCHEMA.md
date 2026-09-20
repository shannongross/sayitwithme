# Database schema

Postgres. Three tables: the English content, the people who contribute, and the
first-language recordings they make. The DDL below is `migrations/001_initial.sql`.

The learner app works entirely in English — picture, English audio, say it back.
First-language audio is an enhancement layered on top, so most phrases have no
recording, and filling that gap is what volunteers do.

## Tables

```sql
CREATE TABLE contributors (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name         TEXT NOT NULL,
  email        TEXT NOT NULL UNIQUE,
  languages    TEXT[] NOT NULL,                      -- ['rhg','en']
  note         TEXT,                                 -- who invited them, and why
  token_hash   TEXT UNIQUE,                          -- hashed invite token
  approved_at  TIMESTAMPTZ,                          -- null until approved
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE english_phrases (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  category            TEXT NOT NULL,                 -- 'clinic'
  text_en             TEXT NOT NULL,
  text_en_normalized  TEXT GENERATED ALWAYS AS
                        (lower(btrim(regexp_replace(text_en, '[^a-zA-Z0-9]+', ' ', 'g')))) STORED,
  image_key           TEXT NOT NULL,                 -- 'img/help.svg'
  contributor_id      UUID REFERENCES contributors(id),
  removed_at          TIMESTAMPTZ,
  created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX english_phrases_dedupe ON english_phrases (text_en_normalized);

CREATE TABLE recordings (
  id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  english_phrase_id  UUID NOT NULL REFERENCES english_phrases(id),
  language_code      TEXT NOT NULL,                  -- 'rhg'
  contributor_id     UUID NOT NULL REFERENCES contributors(id),
  storage_key        TEXT NOT NULL UNIQUE,
  text_native        TEXT,                           -- written first-language text, optional
  removed_at         TIMESTAMPTZ,
  created_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX recordings_one_per_language
  ON recordings (english_phrase_id, language_code)
  WHERE removed_at IS NULL;
```

## Why these columns

**`text_en_normalized` is generated, not authored.** `text_en` carries the real
capitalization and punctuation, which TTS prosody depends on. The normalized form
exists only as a dedupe key, so the database derives it and the two cannot drift.
A second submission of the same English phrase attaches a recording to the existing
row instead of creating a duplicate card.

**Grading needs no column.** Exact sentence matching fails a learner who says
"I need interpreter", which is exactly the person this is for. Instead the grader strips
a fixed set of filler words from `text_en` and checks the learner said the rest — so the
rubric is derived, nothing is authored per phrase, and a contributor is never asked to
mark up their own sentence.

**`category` and `image_key` are required.** A card with no picture is unusable to
someone who cannot read, so `scripts/seed.py` holds back any phrase without one rather
than inserting a row the app would have to hide.

**`contributor_id IS NULL` means seed content.** That is the only marker needed, and
it scopes the seed: `scripts/seed.py` may only upsert rows where `contributor_id IS NULL`,
so re-seeding can never touch contributed content. It upserts on
`text_en_normalized`, which is the stable natural key.

**Contributors are approved individually; their content is not.** `token_hash` is the
invite a partner organization hands out, and `approved_at` is the one gate a person
passes through. After that, what they submit publishes automatically — nobody on the
project speaks Rohingya, so a per-recording review would be theatre.

**`removed_at` is the only takedown mechanism.** Removal is reactive, after a
first-language speaker reports a problem.

**The recordings unique index is partial.** Scoped to `removed_at IS NULL` so removing
a recording frees that phrase+language slot for a replacement instead of blocking it
forever. It serves the per-phrase lookup too, so no separate index is needed.

**`language_code` is a plain column, not a table.** A second oral-only language needs
new rows, not a migration.

## Deliberately absent

Recorded so these are not reintroduced without a reason.

| absent | why |
|---|---|
| `reviews`, approval counts, reviewer roles | contributors are approved, content is not |
| `languages` table, `content_license` | one row and one project-wide decision; the license is in `content/media/ATTRIBUTION.md` |
| `consent_versions` | consent is a static checkbox; the text lives in the repo |
| `lessons` table | `category` is a column; the category tile is the first phrase's picture |
| slugs | generated from arbitrary contributor text, so they need collision handling and go stale when text is edited |
| `chunks`, `easier_phrase_id`, `harder_phrase_id`, `level` | a six-move teaching engine and a difficulty ladder tax every phrase ever authored |
| `key_words`, `accepted_variants` | the grader derives content words from `text_en` by removing filler. A per-phrase override earns its place only when a real phrase turns on a filler word. |
| `image_prompt` | pictures come from a symbol library, not a generator |
| `duration_ms`, `format`, `checksum`, `auto_checks` | derivable from the file, or the result of a check that already gated the insert |
| separate private-original and public-approved copies | without an approval gate there is no window where a recording is held but not served. One processed file, one key. |
| `voice_label` | identifying metadata about a persecuted community, for a feature that does not exist |
| status enums | a nullable timestamp says the same thing; `removed_at IS NULL` is the live set |

## Media

Bytes never go in the database. `image_key` is a path under `content/media`, which the
API serves; `storage_key` will be an object-storage key once volunteers can upload. See
[ARCHITECTURE.md](ARCHITECTURE.md) for the media layout and the submission pipeline.

## Coverage query

The one the contributor screen runs, and the one a progress view reports on:

```sql
SELECT p.*
FROM english_phrases p
LEFT JOIN recordings r
  ON r.english_phrase_id = p.id
 AND r.language_code = 'rhg'
 AND r.removed_at IS NULL
WHERE r.id IS NULL
  AND p.removed_at IS NULL;
```

## Open

- **Consent wording changes.** Without `consent_version` there is no record of who
  agreed to what. Fine while the terms are static.
- **Learner-facing reports.** If learners get a "this sounds wrong" tap, it needs
  somewhere to land; otherwise removal starts with an email.
