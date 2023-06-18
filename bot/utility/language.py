from typing import Literal, get_args

LanguageCode = Literal["en", "uk"]


def is_language_supported(language_code: str) -> bool:
    return language_code in get_args(LanguageCode)


def get_language_name_map() -> dict[LanguageCode, str]:
    return {"en": "English", "uk": "Українська"}
