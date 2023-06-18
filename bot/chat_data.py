from telegram.ext import ContextTypes

from bot.utility.language import LanguageCode


class ChatData:
    def __init__(self, context: ContextTypes) -> None:
        self._context = context

    @property
    def language_code(self) -> LanguageCode:
        return self._context.chat_data.get("language_code", "en")

    @language_code.setter
    def language_code(self, value: LanguageCode) -> None:
        self._context.chat_data["language_code"] = value

    @property
    def show_popular(self) -> bool:
        return self._context.chat_data.get("show_popular", False)

    @show_popular.setter
    def show_popular(self, value: bool) -> None:
        self._context.chat_data["show_popular"] = value
