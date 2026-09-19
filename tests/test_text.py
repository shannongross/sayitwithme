from tutor.text import is_understood, normalize


phrase = {
    "text": "I speak Rohingya. I need an interpreter.",
    "accepted_variants": ["I need an interpreter."],
}


def test_normalize_ignores_case_and_punctuation() -> None:
    assert normalize(" I NEED an interpreter! ") == "i need an interpreter"


def test_accepts_target_and_variant() -> None:
    assert is_understood("I speak Rohingya, I need an interpreter.", phrase)
    assert is_understood("I need an interpreter.", phrase)


def test_rejects_other_words() -> None:
    assert not is_understood("I need a taxi.", phrase)