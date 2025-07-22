from telebot import TeleBot, types
from dotenv import load_dotenv, find_dotenv
from os import environ
from earthquakes_info import find_last_earthquakes, get_coords


load_dotenv(find_dotenv())
telegram_bot_token = environ["TELEGRAM_API"]
yandex_api_key = environ["YANDEX_API"]
bot = TeleBot(telegram_bot_token)
longitude, latitude = 0, 0
radius = 3000


@bot.message_handler(commands=["start", "help"])
def start(message):
    bot.send_message(message.chat.id, """
    Список доступных комманд:

/setplace -> установить своё местоположение (по умолчанию Остров Ноль)
/setradius -> установить радиус в километрах поиска землетрясений (по умолчанию 3000)
/fetch -> получить землетрясения за последнее время
/info -> информация о проекте
/help либо /start -> вывод данного сообщения
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
    qargs = len(args) - 1

    match qargs:
        case 0:
            bot.send_message(message.chat.id, "Вы должны указать название своего населенного пункта!")
        case 1:
            longitude, latitude = get_coords(args[1], yandex_api_key)
            if not longitude or not latitude:
                bot.send_message(message.chat.id, "Место, выбранное вами не было найдено.\nУстановленны координаты 0, 0")
                longitude, latitude = 0, 0
                return None
            bot.send_message(message.chat.id, f"Местоположение было успешно установлено!\nВаши координаты: {latitude} (широта), {longitude} (долгота)")
        case _:
            bot.send_message(message.chat.id, "Вы должны указать лишь один аргумент!")


@bot.message_handler(commands=["setradius"])
def setradius(message):
    global radius
    args = message.text.split(" ")
    qargs = len(args) - 1

    match qargs:
        case 0:
            bot.send_message(message.chat.id, f"Так как радиус не был указан, было задано значение по умолчанию ({radius} км)")
        case 1:
            if not args[1].isdigit():
                bot.send_message(message.chat.id, "Вы должны ввести число!")
                return None
            radius = int(args[1])
            bot.send_message(message.chat.id, f"Успешно установлен радиус на значение {radius} километров!")
        case _:
            bot.send_message(message.chat.id, "Вы должны указать лишь один аргумент!")


@bot.message_handler(commands=["fetch"])
def fetch(message):
    global latitude, longitude, radius
    args = message.text.split(" ")
    qargs = len(args) - 1

    match qargs:
        case 0:
            bot.send_message(message.chat.id, "Вы должны указать за сколько последних дней искать землетрясения!")
        case 1:
            if not args[1].isdigit():
                bot.send_message(message.chat.id, "Вы должны ввести число!")
                return None

            earthquakes = find_last_earthquakes(latitude, longitude, int(args[1]), radius)

            if not len(earthquakes):
                bot.send_message(message.chat.id, "Не было найдено землетрясений по критериям пользователя")
                return None

            bot.send_message(message.chat.id, "Ниже приведен список найденных землетрясений:")
            for earthquake in earthquakes:
                markup = types.InlineKeyboardMarkup()
                button = types.InlineKeyboardButton(text="Карта местности проишествия", url = earthquake["map"])
                markup.add(button)
                bot.send_message(message.chat.id, f"""
                {earthquake["title"]}

Место события -> {earthquake["place"]}
Время события -> {earthquake["date"]}
Расстояние до пользователя ->  {earthquake["distance"]} км

Географическая широта -> {earthquake["latitude"]}
Географическая долгота -> {earthquake["longitude"]}
                """, reply_markup=markup)
        case _:
            bot.send_message(message.chat.id, "Вы должны указать лишь один аргумент!")


def bot_loop():
    bot.polling(none_stop=True)


if __name__ == "__main__":
    bot_loop()