import logging
import os
import sys
from typing import Final

import telegram.error
import tmdbsimple as tmdb
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import CommandHandler, MessageHandler, ApplicationBuilder, filters, ContextTypes


logger = logging.getLogger(__name__)

tmdb.API_KEY = os.getenv("TMDB_API_KEY")

TEMP_LANG: str = "en"
SHOW_POPULAR: bool = True
BASE_POSTER_PATH: Final[str] = "http://image.tmdb.org/t/p/w780"


ANSWER_ALL = {
    "en": "All found films will be shown",
    "uk": "Усі знайдені фільми будуть відображені",
}
ANSWER_POPULAR = {
    "en": "Only the most popular films will be shown",
    "uk": "Тільки айпопулярніші фільми будуть відображені",
}


async def english(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global TEMP_LANG
    TEMP_LANG = "en"
    await update.message.reply_text("Language results are shown in has been changed successfully!/help")


async def ukrainian(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global TEMP_LANG
    TEMP_LANG = "uk"
    await update.message.reply_text("Мову відображення результатів успішно змінено!/help")


async def help_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    change_language = "To change language:\n/en - English" + "\n/uk - Українська"
    filter = (
        "\nTo filter by popularity:\n/showall - "
        + ANSWER_ALL[TEMP_LANG]
        + "\n/showpopular - "
        + ANSWER_POPULAR[TEMP_LANG]
    )
    await update.message.reply_text(change_language + filter)


async def show_popular(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global SHOW_POPULAR
    SHOW_POPULAR = True
    await update.message.reply_text(ANSWER_POPULAR[TEMP_LANG] + "(max = 5)/help")


async def show_all(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global SHOW_POPULAR
    SHOW_POPULAR = False
    await update.message.reply_text(ANSWER_ALL[TEMP_LANG] + "(unlimited)/help")


async def start_messaging(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Привіт, чого бажаєте?/help")


async def query_movies(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    search = tmdb.Search()
    movie_query = update.message.text.lower()
    search.movie(query=movie_query, language=TEMP_LANG)

    if not search.results:
        answer = {"en": "No result. Please, change your query", "uk": "Нічого не знайдено. Будь ласка, змініть запит"}
        await update.message.reply_text(answer[TEMP_LANG] + "/help")

    movie_properties_list = sorted(search.results, key=lambda movie_props: movie_props["popularity"], reverse=True)
    if SHOW_POPULAR:
        movie_properties_list = movie_properties_list[:5]

    for movie_properties in movie_properties_list:
        try:
            poster_path = BASE_POSTER_PATH + movie_properties["poster_path"]
            await update.message.reply_photo(poster_path)
        except TypeError:
            logger.error("Poster path is None")
            await update.message.reply_text("No poster 😞", parse_mode=ParseMode.MARKDOWN)
        except telegram.error.BadRequest:
            logger.error(f"Failed to retrieve poster {poster_path}")
            await update.message.reply_text("No poster 😞", parse_mode=ParseMode.MARKDOWN)

        title = movie_properties["title"]
        release_date = movie_properties["release_date"]
        rating = round(movie_properties["vote_average"], 1)
        overview = movie_properties["overview"]

        key_details = "*" + f"{title}, {release_date}, {rating}/10" + "*" + "🍿"
        movie_info = key_details + "\n" + overview
        await update.message.reply_text(movie_info, parse_mode=ParseMode.MARKDOWN)


app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

app.add_handler(CommandHandler("start", start_messaging))
app.add_handler(CommandHandler("showpopular", show_popular))
app.add_handler(CommandHandler("showall", show_all))
app.add_handler(CommandHandler("help", help_message))
app.add_handler(CommandHandler("en", english))
app.add_handler(CommandHandler("uk", ukrainian))
app.add_handler(MessageHandler(filters.TEXT, query_movies))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    app.run_polling()
