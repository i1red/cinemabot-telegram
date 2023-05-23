import os

import tmdbsimple as tmdb
from telegram.constants import ParseMode
from telegram.ext import CommandHandler, MessageHandler, ApplicationBuilder, filters

tmdb.API_KEY = os.getenv("TMDB_API_KEY")

app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

temp_lang = "en"
show_popular = True

answerAll = {"en": "All found films will be shown", "uk": "Усі знайдені фільми будуть відображені", "zh": "將顯示所有找到的電影"}
answerPopular = {
    "en": "Only the most popular films will be shown",
    "uk": "Тільки айпопулярніші фільми будуть відображені",
    "zh": "只會播放最受歡迎的電影",
}


async def english(update, context):
    global temp_lang
    temp_lang = "en"
    await update.message.reply_text("Language results are shown in has been changed successfully!/help")
    pass


async def ukrainian(update, context):
    global temp_lang
    temp_lang = "uk"
    await update.message.reply_text("Мову відображення результатів успішно змінено!/help")
    pass


async def chinese(update, context):
    global temp_lang
    temp_lang = "zh"
    await update.message.reply_text("語言結果顯示已成功更改!/help")
    pass


async def helpMessage(update, context):
    changeLanguage = "To change language:\n/en - English" + "\n/zh - 中國" + "\n/uk - Українська"
    Filter = (
        "\nTo filter by popularity:\n/showall - "
        + answerAll[temp_lang]
        + "\n/showpopular - "
        + answerPopular[temp_lang]
    )
    await update.message.reply_text(changeLanguage + Filter)
    pass


async def showPopular(update, context):
    global show_popular
    show_popular = True
    await update.message.reply_text(answerPopular[temp_lang] + "(max = 5)/help")
    pass


async def showAll(update, context):
    global show_popular
    show_popular = False
    await update.message.reply_text(answerAll[temp_lang] + "(unlimited)/help")
    pass


async def startMessaging(update, context):
    await update.message.reply_text("Привіт, чого бажаєте?/help")
    pass


async def updateMessage(update, context):
    search = tmdb.Search()
    searched_film = update.message.text.lower()
    search.movie(query=searched_film, language=temp_lang)

    if not search.results:
        answer = {
            "en": "No result. Please, change your query",
            "uk": "Нічого не знайдено. Будь ласка, змініть запит",
            "zh": "沒有結果。 請更改您的查詢",
        }
        await update.message.reply_text(answer[temp_lang] + "/help")
        pass

    res = sorted(search.results, key=lambda k: k["popularity"], reverse=True)

    counter = 0
    k = 0
    for i in res:
        if k == 5 and show_popular == True:
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


app.add_handler(CommandHandler("start", startMessaging))
app.add_handler(CommandHandler("showpopular", showPopular))
app.add_handler(CommandHandler("showall", showAll))
app.add_handler(CommandHandler("help", helpMessage))
app.add_handler(CommandHandler("en", english))
app.add_handler(CommandHandler("uk", ukrainian))
app.add_handler(CommandHandler("zh", chinese))
app.add_handler(MessageHandler(filters.TEXT, updateMessage))


app.run_polling()
