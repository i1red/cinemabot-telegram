import os

import tmdbsimple as tmdb
from telegram.constants import ParseMode
from telegram.ext import CommandHandler, MessageHandler, ApplicationBuilder, filters

tmdb.API_KEY = os.getenv("TMDB_API_KEY")

TEMP_LANG = "en"
SHOW_POPULAR = True

ANSWER_ALL = {
    "en": "All found films will be shown",
    "uk": "Усі знайдені фільми будуть відображені",
}
ANSWER_POPULAR = {
    "en": "Only the most popular films will be shown",
    "uk": "Тільки айпопулярніші фільми будуть відображені",
}


async def english(update, context):
    global TEMP_LANG
    TEMP_LANG = "en"
    await update.message.reply_text("Language results are shown in has been changed successfully!/help")
    pass


async def ukrainian(update, context):
    global TEMP_LANG
    TEMP_LANG = "uk"
    await update.message.reply_text("Мову відображення результатів успішно змінено!/help")
    pass


async def help_message(update, context):
    change_language = "To change language:\n/en - English" + "\n/uk - Українська"
    filter = (
        "\nTo filter by popularity:\n/showall - "
        + ANSWER_ALL[TEMP_LANG]
        + "\n/showpopular - "
        + ANSWER_POPULAR[TEMP_LANG]
    )
    await update.message.reply_text(change_language + filter)
    pass


async def show_popular(update, context):
    global SHOW_POPULAR
    SHOW_POPULAR = True
    await update.message.reply_text(ANSWER_POPULAR[TEMP_LANG] + "(max = 5)/help")
    pass


async def show_all(update, context):
    global SHOW_POPULAR
    SHOW_POPULAR = False
    await update.message.reply_text(ANSWER_ALL[TEMP_LANG] + "(unlimited)/help")
    pass


async def start_messaging(update, context):
    await update.message.reply_text("Привіт, чого бажаєте?/help")
    pass


async def update_message(update, context):
    search = tmdb.Search()
    searched_film = update.message.text.lower()
    search.movie(query=searched_film, language=TEMP_LANG)

    if not search.results:
        answer = {"en": "No result. Please, change your query", "uk": "Нічого не знайдено. Будь ласка, змініть запит"}
        await update.message.reply_text(answer[TEMP_LANG] + "/help")
        pass

    res = sorted(search.results, key=lambda k: k["popularity"], reverse=True)

    counter = 0
    k = 0
    for i in res:
        if k == 5 and SHOW_POPULAR == True:
            break
        name = str(i["title"]).lower()
        if name.find(searched_film) == -1 and counter != 0:
            continue
        if name.find(searched_film) != -1:
            counter += 1
        film_info = (
            "\t"
            + "*"
            + str(i["title"])
            + ", "
            + str(i["release_date"])
            + ", "
            + str(i["vote_average"])
            + "/10"
            + "*"
            + "\U0001F37F"
            + "\n\t"
            + str(i["overview"])
        )
        poster_path = "http://image.tmdb.org/t/p/w780" + str(i["poster_path"])
        await update.message.reply_text(film_info, parse_mode=ParseMode.MARKDOWN)
        await update.message.reply_photo(poster_path)
        k += 1
    pass


app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

app.add_handler(CommandHandler("start", start_messaging))
app.add_handler(CommandHandler("showpopular", show_popular))
app.add_handler(CommandHandler("showall", show_all))
app.add_handler(CommandHandler("help", help_message))
app.add_handler(CommandHandler("en", english))
app.add_handler(CommandHandler("uk", ukrainian))
app.add_handler(MessageHandler(filters.TEXT, update_message))


if __name__ == "__main__":
    app.run_polling()
