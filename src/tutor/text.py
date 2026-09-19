import re


def normalize(text: str) -> str:
    cleaned = re.sub(r"[^a-z0-9 ]", " ", text.lower())
    return " ".join(cleaned.split())


def is_understood(transcript: str, phrase: dict) -> bool:
    accepted = [phrase["text"], *phrase["accepted_variants"]]
    return normalize(transcript) in {normalize(text) for text in accepted}