import base64
import csv
import sys

import httpx

from api import config
from api.text import slug

model = "gemini-3.1-flash-image"

# One style for every card, so phrases look like they belong to one app.
style = (
    "Flat vector illustration, warm muted palette, soft rounded shapes, plain light "
    "background, square composition. No text, letters, numbers or signage anywhere. "
    "The main figure is an adult South Asian woman in a headscarf and long dress. "
    "Scene: "
)


def generate(client: httpx.Client, scene: str) -> bytes:
    response = client.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        json={
            "contents": [{"parts": [{"text": style + scene}]}],
            "generationConfig": {"responseModalities": ["IMAGE"]},
        },
        headers={"x-goog-api-key": config.gemini_api_key},
    )
    response.raise_for_status()
    parts = response.json()["candidates"][0]["content"]["parts"]
    image = next(part["inlineData"] for part in parts if "inlineData" in part)
    return base64.b64decode(image["data"])


def illustrate(limit: int | None) -> None:
    if not config.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is required")

    rows = list(
        csv.DictReader(config.phrases_csv.read_text(encoding="utf-8").splitlines())
    )
    have = {p.stem for p in config.images_dir.iterdir() if p.is_file()}
    generated, skipped = 0, 0

    with (
        config.manifest.open("a", encoding="utf-8", newline="") as handle,
        httpx.Client(timeout=120) as client,
    ):
        record = csv.writer(handle)
        for row in rows:
            if not row["scene"]:
                continue
            name = slug(row["text_en"])
            if name in have:
                skipped += 1
                continue
            if limit is not None and generated >= limit:
                break

            file = f"{name}.png"
            (config.images_dir / file).write_bytes(generate(client, row["scene"]))

            # Written per image so a crash leaves files and provenance in step.
            record.writerow([file, row["text_en"], model, "generated", row["scene"]])
            handle.flush()
            generated += 1
            print(" ", file)

    print(f"generated {generated}, skipped {skipped}")


if __name__ == "__main__":
    illustrate(int(sys.argv[1]) if len(sys.argv) > 1 else None)
