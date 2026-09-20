import asyncio
import csv

import asyncpg

from api import config
from api.text import slug

images = config.content_dir / "media" / "img"


def image_key(text: str) -> str | None:
    for path in sorted(images.glob(f"{slug(text)}.*")):
        return f"img/{path.name}"
    return None


async def seed() -> None:
    path = config.content_dir / "phrases.csv"
    rows = list(csv.DictReader(path.read_text(encoding="utf-8").splitlines()))
    pool = await asyncpg.create_pool(config.database_url)

    loaded, waiting = 0, []
    for row in rows:
        key = image_key(row["text_en"])
        # A phrase with no picture is not usable, so it waits here until one exists.
        if key is None:
            waiting.append(row["text_en"])
            continue
        await pool.execute(
            """
            INSERT INTO english_phrases (category, text_en, image_key)
            VALUES ($1, $2, $3)
            ON CONFLICT (text_en_normalized) DO UPDATE
            SET category = EXCLUDED.category, image_key = EXCLUDED.image_key
            WHERE english_phrases.contributor_id IS NULL
            """,
            row["category"],
            row["text_en"],
            key,
        )
        loaded += 1

    await pool.close()
    print(f"loaded {loaded}, waiting on a picture {len(waiting)}")


if __name__ == "__main__":
    asyncio.run(seed())
