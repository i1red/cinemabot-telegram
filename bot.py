import telegram
import tmdbsimple as tmdb
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

tmdb.API_KEY = 'c8614c46f861944cdcedd2e79fdd1a20'

updater = Updater('718242667:AAEUaltXy6raqTmsRxBtVtJvWJNmzkgoW5I')
dispatcher = updater.dispatcher

temp_lang = 'en'
show_popular = True

answerAll = {'en': 'All found films will be shown', 'uk' : 'Усі знайдені фільми будуть відображені', 'zh' : '將顯示所有找到的電影', 'ru' : 'Все найденые фыльмы будут отображены'}
answerPopular = {'en': 'Only the most popular films will be shown', 'uk' : 'Тільки айпопулярніші фільми будуть відображені', 'zh' : '只會播放最受歡迎的電影', 'ru' : 'Только самые популярные фыльмы будут отображены'}

def english(bot, update):
    global temp_lang
    temp_lang = 'en'
    bot.send_message(chat_id=update.message.chat_id, text='Language results are shown in has been changed successfully!/help')
    pass

def ukrainian(bot, update):
    global temp_lang
    temp_lang = 'uk'
    bot.send_message(chat_id=update.message.chat_id, text='Мову відображення результатів успішно змінено!/help')
    pass

def chinese(bot, update):
    global temp_lang
    temp_lang = 'zh'
    bot.send_message(chat_id=update.message.chat_id, text='語言結果顯示已成功更改!/help')
    pass

def russian(bot, update):
    global temp_lang
    temp_lang = 'ru'
    bot.send_message(chat_id=update.message.chat_id, text='Язык выдачи результатов успешно изменен!/help')
    pass

def helpMessage(bot, update):
    changeLanguage = 'To change language:\n/en - English' + '\n/zh - 中國' + '\n/uk - Українська' + '\n/ru - Русский'
    Filter = '\nTo filter by popularity:\n/showall - ' + answerAll[temp_lang] + '\n/showpopular - ' + answerPopular[temp_lang] 
    bot.send_message(chat_id=update.message.chat_id, text=changeLanguage+Filter)
    pass

def showPopular(bot, update):
    global show_popular
    show_popular = True
    bot.send_message(chat_id=update.message.chat_id, text=answerPopular[temp_lang] + '(max = 5)/help')
    pass

def showAll(bot, update):
    global show_popular
    show_popular = False
    bot.send_message(chat_id=update.message.chat_id, text=answerAll[temp_lang] + '(unlimited)/help')
    pass

def startMessaging(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text='Здравствуйте, чего желаете?/help')
    pass

def updateMessage(bot, update):
    message_id = update.message.chat_id
    search = tmdb.Search()
    searched_film = update.message.text.lower()
    search.movie(query=searched_film, language=temp_lang)

    if not search.results:
        answer = {'en': 'No result. Please, change your query', 'uk' : 'Нічого не знайдено. Будь ласка, змініть запит', 'zh' : '沒有結果。 請更改您的查詢', 'ru' : 'Ничего не найдено. Пожалуйста измените запрос'}
        bot.send_message(chat_id=message_id, text=answer[temp_lang] + '/help')
        pass
    
    res = sorted(search.results, key = lambda k: k['popularity'], reverse = True)

    counter = 0
    k=0
    for i in res:
        if k == 5 and show_popular == True:
            break
        name = str(i['title']).lower()
        if name.find(searched_film) == -1 and counter != 0:
            continue
        if name.find(searched_film) != -1 :
            counter+=1
        film_info = '\t'  + "*" + str(i['title'])  + ', ' + str(i['release_date']) + ', ' + str(i['vote_average']) + '/10' + "*" + u"\U0001F37F" + '\n\t' + str(i['overview'])
        poster_path = 'http://image.tmdb.org/t/p/w780' + str(i['poster_path'])
        bot.send_message(chat_id=message_id, text=film_info, parse_mode=telegram.ParseMode.MARKDOWN)
        bot.send_photo(chat_id=message_id, photo=poster_path)
        k+=1
    pass

start_command_handler = CommandHandler('start', startMessaging)
showPopular_command_handler = CommandHandler('showpopular', showPopular)
showAll_command_handler = CommandHandler('showall', showAll)
help_command_handler = CommandHandler('help', helpMessage)
english_command_handler = CommandHandler('en', english)
ukrainian_command_handler = CommandHandler('uk', ukrainian)
chinese_command_handler = CommandHandler('zh', chinese)
russian_command_handler = CommandHandler('ru', russian)
text_message_handler = MessageHandler(Filters.text, updateMessage)

dispatcher.add_handler(start_command_handler)
dispatcher.add_handler(showPopular_command_handler)
dispatcher.add_handler(showAll_command_handler)
dispatcher.add_handler(help_command_handler)
dispatcher.add_handler(english_command_handler)
dispatcher.add_handler(ukrainian_command_handler)
dispatcher.add_handler(russian_command_handler)
dispatcher.add_handler(chinese_command_handler)
dispatcher.add_handler(text_message_handler)

updater.start_polling(clean=True)

updater.idle()
