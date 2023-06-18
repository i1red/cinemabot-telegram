import logging
import os
import sys

import telegram.error
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import CommandHandler, MessageHandler, ApplicationBuilder, filters, ContextTypes

from bot.chat_data import ChatData
from bot.movie import search_movies
from bot.utility.language import is_language_supported, get_language_name_map
from bot.utility.message import get_message

logger = logging.getLogger(__name__)


async def change_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_data = ChatData(context)

    try:
        (new_language_code,) = context.args
    except TypeError:
        message = get_message("Required arguments were not provided", chat_data.language_code)
        await update.message.reply_text(message + "/help")
        return
    except ValueError:
        message = get_message("Incorrect number of arguments", chat_data.language_code)
        await update.message.reply_text(message + "/help")
        return

    if not is_language_supported(new_language_code):
        message = get_message("Language not supported", chat_data.language_code)
        await update.message.reply_text(message + "/help")
        return

    chat_data.language_code = new_language_code
    message = get_message("The language for displaying results has been changed successfully!", new_language_code)
    await update.message.reply_text(message + "/help")


async def help_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_data = ChatData(context)

    change_language = (
        get_message("Change language", chat_data.language_code)
        + "\n"
        + "\n".join(f"/lang {lang_code} - {lang_name}" for lang_code, lang_name in get_language_name_map().items())
    )
    filter = (
        get_message("Filter by popularity", chat_data.language_code)
        + "\n"
        + "/show_all - "
        + get_message("All found films will be shown", chat_data.language_code)
        + "\n"
        + "/show_popular - "
        + get_message("Only the most popular films will be shown", chat_data.language_code)
        + "\n"
    )
    await update.message.reply_text(change_language + "\n" + filter)


async def show_popular(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_data = ChatData(context)

    chat_data.show_popular = True

    message = get_message("Only the most popular films will be shown", chat_data.language_code)
    await update.message.reply_text(message + "/help")


async def show_all(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_data = ChatData(context)

    chat_data.show_popular = False

    message = get_message("All found films will be shown", chat_data.language_code)
    await update.message.reply_text(message + "/help")


async def start_messaging(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_data = ChatData(context)

    message = get_message("Hi, what are you looking for?", chat_data.language_code)
    await update.message.reply_text(message + "/help")


async def query_movies(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_data = ChatData(context)

    movie_query = update.message.text.lower()
    movie_properties_list = search_movies(query=movie_query, language_code=chat_data.language_code)

    if not movie_properties_list:
        message = get_message("No result. Please, change your query", chat_data.language_code)
        await update.message.reply_text(message + "/help")

    movie_properties_list = sorted(movie_properties_list, key=lambda movie_props: movie_props.popularity, reverse=True)
    if chat_data.show_popular:
        movie_properties_list = movie_properties_list[:5]

    for movie_properties in movie_properties_list:
        if movie_properties.poster_uri is None:
            logger.info("Poster uri is None")
            message = get_message("No poster😞", chat_data.language_code)
            await update.message.reply_text(message + "", parse_mode=ParseMode.MARKDOWN)

        try:
            await update.message.reply_photo(movie_properties.poster_uri)
        except telegram.error.BadRequest:
            logger.error(f"Failed to retrieve poster {movie_properties.poster_uri}")
            message = get_message("No poster😞", chat_data.language_code)
            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

        key_details = (
            "*" + f"{movie_properties.title}, {movie_properties.release_date}, {movie_properties.rating}/10" + "*" + "🍿"
        )
        movie_info = key_details + "\n" + movie_properties.overview
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
