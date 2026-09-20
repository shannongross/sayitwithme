from uuid import UUID

from asyncpg import Pool


async def list_categories(pool: Pool) -> list[dict]:
    # Categories appear in the order their first phrase was seeded: the CSV controls it.
    rows = await pool.fetch(
        """
        SELECT category, image_key FROM (
            SELECT DISTINCT ON (category) category, image_key, created_at
            FROM english_phrases
            WHERE removed_at IS NULL
            ORDER BY category, created_at
        ) first
        ORDER BY created_at
        """
    )
    return [
        {"id": row["category"], "image_url": f"/media/{row['image_key']}"}
        for row in rows
    ]


async def list_phrases(pool: Pool, category: str) -> list[dict]:
    rows = await pool.fetch(
        """
        SELECT id, text_en, image_key
        FROM english_phrases
        WHERE category = $1 AND removed_at IS NULL
        ORDER BY created_at
        """,
        category,
    )
    return [
        {
            "id": str(row["id"]),
            "text": row["text_en"],
            "image_url": f"/media/{row['image_key']}",
        }
        for row in rows
    ]


async def find_phrase_text(pool: Pool, phrase_id: UUID) -> str | None:
    return await pool.fetchval(
        "SELECT text_en FROM english_phrases WHERE id = $1 AND removed_at IS NULL",
        phrase_id,
    )
