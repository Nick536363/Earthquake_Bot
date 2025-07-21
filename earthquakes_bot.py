from telebot import TeleBot, types
from dotenv import load_dotenv, find_dotenv
from os import environ
from earthquakes_info import find_last_earthquakes, get_coords


load_dotenv(find_dotenv())
telegram_bot_token = environ["TELEGRAM_API"]
yandex_api_key = environ["YANDEX_API"]
bot = TeleBot(telegram_bot_token)
longitude, latitude = 0, 0


@bot.message_handler(commands=["start", "help"])
def start(message):
    bot.send_message(message.chat.id, """
    Список доступных комманд:

/setplace - установить своё местоположение
/fetch - получить землетрясения за последнее время
/info - информация о проекте
/help либо /start - вывод данного сообщения
    """)


@bot.message_handler(commands=["info"])
def info(message):
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text="Ссылка на репозиторий", url = "https://github.com/Nick536363/Earthquake_Bot")
    markup.add(button)
    bot.send_message(message.chat.id, """
    Информация о проекте:

Тимлид: Nick536363
Разработчик бота: yatoro-asu
    """, reply_markup=markup)


@bot.message_handler(commands=["setplace"])
def setplace(message):
    global latitude, longitude
    args =  message.text.split(" ")
    qargs = len(args)-1
    match qargs:
        case 0:
            bot.send_message(message.chat.id, "Вы должны указать название своего населенного пункта!")
        case 1:
            longitude, latitude = get_coords(args[1], yandex_api_key)
            if not longitude or not latitude:
                bot.send_message(message.chat.id, "Место, выбранное вами не было найдено.\nУстановленны координаты 0, 0")
                longitude, latitude = 0, 0
                return None
            bot.send_message(message.chat.id, f"Местоположение было успешно установлено!\nВаши координаты: {latitude} (ширина), {longitude} (долгота)")
        case _:
            bot.send_message(message.chat.id, "Вы должны указать лишь один аргумент!")


def bot_loop():
    bot.polling(none_stop=True)


if __name__ == "__main__":
    bot_loop()