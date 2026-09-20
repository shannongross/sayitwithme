import csv
import time
from pathlib import Path

import httpx

from api import config
from api.text import slug

images = config.content_dir / "media" / "img"
manifest = config.content_dir / "media" / "MANIFEST.csv"

base_url = "https://globalsymbols.com/api/v1"
# One visual family only: a mixed-style set reads worse than a smaller consistent one.
symbolsets = ["mulberry", "additional-mulberry-symbols", "corona-symbols"]


def search(client: httpx.Client, word: str, symbolset: str) -> list[dict]:
    for attempt in range(6):
        response = client.get(
            f"{base_url}/labels/search",
            params={"query": word, "language": "eng", "symbolset": symbolset},
        )
        if response.status_code != 429:
            response.raise_for_status()
            return response.json()
        time.sleep(2**attempt)
    raise RuntimeError(f"rate limited looking up {word!r}")


def find(client: httpx.Client, word: str) -> tuple[str, dict] | None:
    # Exact label only. A near match is a guess, and a wrong picture is worse than none.
    for symbolset in symbolsets:
        for hit in search(client, word, symbolset):
            if hit["text"].strip().lower() == word.strip().lower():
                return symbolset, hit
    return None


def fetch() -> None:
    path = config.content_dir / "phrases.csv"
    rows = list(csv.DictReader(path.read_text(encoding="utf-8").splitlines()))
    images.mkdir(parents=True, exist_ok=True)

    have = {p.stem for p in images.iterdir() if p.is_file()}
    downloaded, missing = 0, []

    fresh = not manifest.exists()
    with (
        manifest.open("a", encoding="utf-8", newline="") as handle,
        httpx.Client(timeout=30, follow_redirects=True) as client,
    ):
        record = csv.writer(handle)
        if fresh:
            record.writerow(["file", "text_en", "symbolset", "license", "source_url"])

        for row in rows:
            word = row["text_en"]
            name = slug(word)
            if name in have:
                continue

            match = find(client, word)
            if match is None:
                missing.append(word)
                continue

            symbolset, hit = match
            url = hit["picto"]["image_url"]
            file = f"{name}{Path(url).suffix or '.svg'}"
            (images / file).write_bytes(client.get(url).content)

            # Written per download so a crash leaves files and attribution in step.
            record.writerow([file, word, symbolset, "CC BY-SA 4.0", url])
            handle.flush()
            downloaded += 1

    print(f"downloaded {downloaded}, skipped {len(have)}, unmatched {len(missing)}")
    for word in missing:
        print("  no exact label:", word)


if __name__ == "__main__":
    fetch()
