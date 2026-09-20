import re

# Words whose absence does not change whether a listener would understand.
filler = {
    "a", "an", "the", "i", "you", "it",
    "is", "am", "are", "to", "of", "and", "my", "me",
}


def normalize(text: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", text.lower()).split())


def slug(text: str) -> str:
    return normalize(text).replace(" ", "-")


def is_understood(transcript: str, text: str) -> bool:
    words = set(normalize(text).split())
    # A target made only of filler has to be said in full, or anything would pass.
    needed = words - filler or words
    return needed <= set(normalize(transcript).split())
