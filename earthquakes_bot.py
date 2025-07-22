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

def get_users_coords(message):
    global latitude, longitude
    place = message.text
    longitude, latitude = get_coords(place, yandex_api_key)
    if not longitude or not latitude:
        bot.send_message(message.chat.id, "Место не было найдено!\nУстановлены координаты по умолчанию (0, 0)")
        longitude, latitude = 0, 0
        return None
    bot.send_message(message.chat.id, f"Координаты успешно установлены!\n{latitude} (широта), {longitude} (долгота)")


def get_search_radius(message):
    global radius
    argument = message.text
    if len(argument.split()) > 1:
        bot.send_message(message.chat.id, "Вы должны указать только одно число!")
        return None
    elif not argument.isdigit():
        bot.send_message(message.chat.id, "Вы должны указать число!")
        return None
    elif int(argument) > 20001:
        bot.send_message(message.chat.id, "Максимальный радиус - 21.000 км!")
        return None
    radius = int(argument)
    bot.send_message(message.chat.id, f"Радиус поиска установлен на значение {radius} км.")


def get_last_earthquakes(message):
    global longitude, latitude, radius
    argument = message.text
    if len(argument.split()) > 1:
        bot.send_message(message.chat.id, "Вы должны указать только одно число!")
        return None
    elif not argument.isdigit():
        bot.send_message(message.chat.id, "Вы должны указать число!")
        return None

    earthquakes = find_last_earthquakes(latitude, longitude, int(argument), radius)

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


@bot.message_handler(commands=["start", "help"])
def start(message):
    markup = types.ReplyKeyboardMarkup()
    setplace_button = types.KeyboardButton("Установить местоположение")
    setradius_button = types.KeyboardButton("Установить радиус поиска")
    fetch_button = types.KeyboardButton("Найти землетрясения")
    info_button = types.KeyboardButton("Информация о проекте")
    markup.add(setplace_button, setradius_button, fetch_button, info_button)
    bot.send_message(message.chat.id, """
    Список доступных комманд:

/setplace -> установить своё местоположение (по умолчанию Остров Ноль)
/setradius -> установить радиус в километрах поиска землетрясений (по умолчанию 3000)
/fetch -> получить землетрясения за последнее время
/info -> информация о проекте
/help либо /start -> вывод данного сообщения
    """, reply_markup=markup)


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
    bot.send_message(message.chat.id, "Пожалуйста, введите название своего населенного пункта (город, поселок, деревня и т.п.).")
    bot.register_next_step_handler(message, get_users_coords)
    

@bot.message_handler(commands=["setradius"])
def setradius(message):
    bot.send_message(message.chat.id, "Пожалуйста, введите радиус поиска землетрясения в километрах (20.001 максимально)")
    bot.register_next_step_handler(message, get_search_radius)


@bot.message_handler(commands=["fetch"])
def fetch(message):
    bot.send_message(message.chat.id, "Пожалуйста, укажите за сколько последних дней вы хотите найти землетрясения")
    bot.register_next_step_handler(message, get_last_earthquakes)


def bot_loop():
    bot.polling(none_stop=True)


if __name__ == "__main__":
    bot_loop()