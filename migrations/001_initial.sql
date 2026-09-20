CREATE TABLE contributors (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name         TEXT NOT NULL,
  email        TEXT NOT NULL UNIQUE,
  languages    TEXT[] NOT NULL,
  note         TEXT,
  token_hash   TEXT UNIQUE,
  approved_at  TIMESTAMPTZ,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE english_phrases (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  category            TEXT NOT NULL,
  text_en             TEXT NOT NULL,
  text_en_normalized  TEXT GENERATED ALWAYS AS
                        (lower(btrim(regexp_replace(text_en, '[^a-zA-Z0-9]+', ' ', 'g')))) STORED,
  image_key           TEXT NOT NULL,
  contributor_id      UUID REFERENCES contributors(id),
  removed_at          TIMESTAMPTZ,
  created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX english_phrases_dedupe ON english_phrases (text_en_normalized);

CREATE TABLE recordings (
  id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  english_phrase_id  UUID NOT NULL REFERENCES english_phrases(id),
  language_code      TEXT NOT NULL,
  contributor_id     UUID NOT NULL REFERENCES contributors(id),
  storage_key        TEXT NOT NULL UNIQUE,
  text_native        TEXT,
  removed_at         TIMESTAMPTZ,
  created_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Partial, so removing a recording frees the slot for a replacement.
CREATE UNIQUE INDEX recordings_one_per_language
  ON recordings (english_phrase_id, language_code)
  WHERE removed_at IS NULL;
