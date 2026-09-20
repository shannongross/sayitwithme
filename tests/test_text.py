from api.text import is_understood, normalize

target = "I speak Rohingya. I need an interpreter."


def test_normalize_ignores_case_and_punctuation() -> None:
    assert normalize(" I NEED an interpreter! ") == "i need an interpreter"


def test_accepts_dropped_filler_words() -> None:
    assert is_understood("I speak Rohingya, I need an interpreter.", target)
    assert is_understood("speak rohingya need interpreter", target)


def test_accepts_extra_words() -> None:
    assert is_understood("I speak Rohingya and I need an interpreter please.", target)


def test_a_target_of_only_filler_still_has_to_be_said() -> None:
    assert is_understood("me", "me")
    assert not is_understood("", "me")


def test_rejects_missing_content_words() -> None:
    assert not is_understood("I need a taxi.", target)
    assert not is_understood("I need an interpreter.", target)
