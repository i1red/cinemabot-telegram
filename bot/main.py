import logging
import os
import sys
from typing import Final

import telegram.error
import tmdbsimple as tmdb
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import CommandHandler, MessageHandler, ApplicationBuilder, filters, ContextTypes

from bot.utility.language import is_language_supported, get_language_name_map, LanguageCode
from bot.utility.message import get_message

logger = logging.getLogger(__name__)

tmdb.API_KEY = os.getenv("TMDB_API_KEY")

DEFAULT_LANGUAGE_CODE: Final[LanguageCode] = "en"
DEFAULT_SHOW_POPULAR: bool = False
BASE_POSTER_PATH: Final[str] = "http://image.tmdb.org/t/p/w780"


async def change_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    language_code = context.chat_data.get("language_code", DEFAULT_LANGUAGE_CODE)

    try:
        (new_language,) = context.args
    except TypeError:
        message = get_message("Required arguments were not provided", language_code)
        await update.message.reply_text(message + "/help")
        return
    except ValueError:
        message = get_message("Incorrect number of arguments", language_code)
        await update.message.reply_text(message + "/help")
        return

    if not is_language_supported(new_language):
        message = get_message("Language not supported", language_code)
        await update.message.reply_text(message + "/help")
        return

    context.chat_data["language_code"] = new_language
    message = get_message("The language for displaying results has been changed successfully!", new_language)
    await update.message.reply_text(message + "/help")


async def help_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    language_code = context.chat_data.get("language_code", DEFAULT_LANGUAGE_CODE)

    change_language = (
        get_message("Change language", language_code)
        + "\n"
        + "\n".join(f"/lang {lang_code} - {lang_name}" for lang_code, lang_name in get_language_name_map().items())
    )
    filter = (
        get_message("Filter by popularity", language_code)
        + "\n"
        + "/show_all - "
        + get_message("All found films will be shown", language_code)
        + "\n"
        + "/show_popular - "
        + get_message("Only the most popular films will be shown", language_code)
        + "\n"
    )
    await update.message.reply_text(change_language + "\n" + filter)


async def show_popular(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    language_code = context.chat_data.get("language_code", DEFAULT_LANGUAGE_CODE)

    context.chat_data["show_popular"] = True

    message = get_message("Only the most popular films will be shown", language_code)
    await update.message.reply_text(message + "(max = 5)/help")


async def show_all(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    language_code = context.chat_data.get("language_code", DEFAULT_LANGUAGE_CODE)

    context.chat_data["show_popular"] = False

    message = get_message("All found films will be shown", language_code)
    await update.message.reply_text(message + "(unlimited)/help")


async def start_messaging(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    language_code = context.chat_data.get("language_code", DEFAULT_LANGUAGE_CODE)

    message = get_message("Hi, what are you looking for?", language_code)
    await update.message.reply_text(message + "/help")


async def query_movies(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    language_code = context.chat_data.get("language_code", DEFAULT_LANGUAGE_CODE)
    show_popular = context.chat_data.get("show_popular", DEFAULT_SHOW_POPULAR)

    search = tmdb.Search()
    movie_query = update.message.text.lower()
    search.movie(query=movie_query, language=language_code)

    if not search.results:
        message = get_message("No result. Please, change your query", language_code)
        await update.message.reply_text(message + "/help")

    movie_properties_list = sorted(search.results, key=lambda movie_props: movie_props["popularity"], reverse=True)
    if show_popular:
        movie_properties_list = movie_properties_list[:5]

    for movie_properties in movie_properties_list:
        try:
            poster_path = BASE_POSTER_PATH + movie_properties["poster_path"]
            await update.message.reply_photo(poster_path)
        except TypeError:
            logger.error("Poster path is None")
            message = get_message("No poster", language_code)
            await update.message.reply_text(message + "😞", parse_mode=ParseMode.MARKDOWN)
        except telegram.error.BadRequest:
            logger.error(f"Failed to retrieve poster {poster_path}")
            message = get_message("No poster", language_code)
            await update.message.reply_text(message + "😞", parse_mode=ParseMode.MARKDOWN)

        title = movie_properties["title"]
        release_date = movie_properties["release_date"]
        rating = round(movie_properties["vote_average"], 1)
        overview = movie_properties["overview"]

        key_details = "*" + f"{title}, {release_date}, {rating}/10" + "*" + "🍿"
        movie_info = key_details + "\n" + overview
        await update.message.reply_text(movie_info, parse_mode=ParseMode.MARKDOWN)


app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

app.add_handler(CommandHandler("start", start_messaging))
app.add_handler(CommandHandler("show_popular", show_popular))
app.add_handler(CommandHandler("show_all", show_all))
app.add_handler(CommandHandler("help", help_message))
app.add_handler(CommandHandler("lang", change_language))
app.add_handler(MessageHandler(filters.TEXT, query_movies))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    app.run_polling()
