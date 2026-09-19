import json
from pathlib import Path


root = Path(__file__).parents[2]


def load_lesson() -> dict:
    return json.loads((root / "content" / "lesson.json").read_text(encoding="utf-8"))