import gettext
import os
from typing import Final, get_args
from gettext import GNUTranslations

from bot.utility.language import LanguageCode

PROJECT_ROOT_DIR: Final[str] = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
LOCALE_DIR: Final[str] = os.path.join(PROJECT_ROOT_DIR, "locale")


def _load_translations() -> dict[LanguageCode, GNUTranslations]:
    return {
        language: gettext.translation(domain="messages", localedir=LOCALE_DIR, languages=[language])
        for language in get_args(LanguageCode)
    }


_TRANSLATIONS: Final[dict[LanguageCode, GNUTranslations]] = _load_translations()


def get_message(message_id: str, language_code: LanguageCode) -> str:
    return _TRANSLATIONS[language_code].gettext(message_id)
