import asyncio
import csv

import asyncpg

from api import config
from api.text import slug


def image_key(text: str) -> str | None:
    for path in sorted(config.images_dir.glob(f"{slug(text)}.*")):
        return f"img/{path.name}"
    return None


async def seed() -> None:
    rows = list(
        csv.DictReader(config.phrases_csv.read_text(encoding="utf-8").splitlines())
    )
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
