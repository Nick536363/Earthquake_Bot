from telebot import TeleBot, types
from dotenv import load_dotenv, find_dotenv
from os import environ
from earthquakes_info import find_last_earthquakes, track_new_earthquakes, get_coords


load_dotenv(find_dotenv())
telegram_bot_token = environ["TELEGRAM_API"]
yandex_api_key = environ["YANDEX_API"]
bot = TeleBot(telegram_bot_token)
longitude, latitude = 0, 0
radius = 3000
tracking_new_eq = False


def send_eq_data(message, earthquake: dict):
    # Отправка сообщения с данными о землетрясении
    markup = types.InlineKeyboardMarkup(row_width=1)
    map_button = types.InlineKeyboardButton(text="🗺 Карта события", url = earthquake["map"])
    region_button = types.InlineKeyboardButton(text="🧭 Региональная информация", url = earthquake["region-info"])
    markup.add(map_button, region_button)
    bot.send_message(message.chat.id, f"""
📝 {earthquake["title"]}

🚩 Место события -> {earthquake["place"]}
🕘 Время события по UTC -> {earthquake["date"]}
↔️ Расстояние до пользователя ->  {earthquake["distance"]} км

🌐↔️ Географическая широта -> {earthquake["latitude"]}
🌐↕ Географическая долгота -> {earthquake["longitude"]}
                """, reply_markup=markup)


def get_users_coords(message):
    # Установка координат с помощью функции из earthquakes_info.py
    global latitude, longitude
    place = message.text
    longitude, latitude = get_coords(place, yandex_api_key)
    if not longitude or not latitude:
        bot.send_message(message.chat.id, "Место не было найдено!\nУстановлены координаты по умолчанию (0, 0)")
        longitude, latitude = 0, 0
        return None
    bot.send_message(message.chat.id, f"Координаты успешно установлены!\n{latitude} (широта), {longitude} (долгота)")


def get_search_radius(message):
    # Установка значения максимального радиуса
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
    # Отправка пользователю землетрясений за последние N дней
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
        send_eq_data(message, earthquake)


# Далее в основном идут функции-обработчики. Это значит что дальше в основном будут "триггеры" на команды пользователя, которые вызывают функции приведенные выше.
# Но также будут и функции-обработчики, которые не вызывают других функций, а делают всё "сами"


@bot.message_handler(commands=["start", "help"])
def start(message):
    # Функция показывающая все доступные команды и отрисовывающая кнопки
    markup = types.ReplyKeyboardMarkup()
    setplace_button = types.KeyboardButton("📍 Установить местоположение") 
    setradius_button = types.KeyboardButton("⭕ Установить радиус поиска")
    fetch_button = types.KeyboardButton("🌎 Найти землетрясения")
    info_button = types.KeyboardButton("ℹ️ Информация о проекте")
    track_button = types.KeyboardButton("🔎 Отслеживать землетрясения")
    untrack_button = types.KeyboardButton("❌ Не отслеживать землетрясения")
    markup.add(setplace_button, setradius_button, fetch_button, track_button, untrack_button, info_button)
    bot.send_message(message.chat.id, """
    Список доступных комманд:

/setplace -> установить своё местоположение (по умолчанию Остров Ноль)
/setradius -> установить радиус в километрах поиска землетрясений (по умолчанию 3000)
/fetch -> получить землетрясения за последнее время
/track -> отслеживать новые землетрясения
/untrack -> перестать отслеживать новые землетрясения
/info -> информация о проекте
/help либо /start -> вывод данного сообщения
    """, reply_markup=markup)


@bot.message_handler(commands=["info"])
def info(message):
    # Функция показывающая информацию о проекте
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text="📩 Ссылка на репозиторий", url = "https://github.com/Nick536363/Earthquake_Bot")
    markup.add(button)
    bot.send_message(message.chat.id, """
    Информация о проекте:

Ведущий программист: Nick536363
    """, reply_markup=markup)


@bot.message_handler(commands=["setplace"])
def setplace(message):
    # Функция для получения названия населенного пункта от пользователя
    bot.send_message(message.chat.id, "Пожалуйста, введите название своего населенного пункта (город, поселок, деревня и т.п.).")
    bot.register_next_step_handler(message, get_users_coords)
    

@bot.message_handler(commands=["setradius"])
def setradius(message):
    # Функция для получения максимального радиуса от пользователя
    bot.send_message(message.chat.id, "Пожалуйста, введите радиус поиска землетрясения в километрах (20.001 максимально)")
    bot.register_next_step_handler(message, get_search_radius)


@bot.message_handler(commands=["fetch"])
def fetch(message):
    # Функция для получения значения от пользователя, за сколько последних дней искать землетрясения 
    bot.send_message(message.chat.id, "Пожалуйста, укажите за сколько последних дней вы хотите найти землетрясения")
    bot.register_next_step_handler(message, get_last_earthquakes)


@bot.message_handler(commands=["track"])
def track(message):
    # Функция для начала отслеживания землетрясений
    global latitude, longitude, radius, tracking_new_eq
    if tracking_new_eq:
        bot.send_message(message.chat.id, "Вы уже отслеживаете новые землетрясения!")
        return None
    tracking_new_eq = True
    bot.send_message(message.chat.id, "Теперь новые землетрясения будут приходить Вам!")
    while tracking_new_eq:
        new_earthquakes = track_new_earthquakes(latitude, longitude, radius, tracking_new_eq)
        bot.send_message(message.chat.id, "Новое событие!")
        for earthquake in new_earthquakes:
            send_eq_data(message, earthquake)


@bot.message_handler(commands=["untrack"])
def untrack(message):
    # Функция для заканчивания отслеживания землетрясений
    global tracking_new_eq
    if not tracking_new_eq:
        bot.send_message(message.chat.id, "Вы не отслеживаете новые землетрясения!")
        return None
    tracking_new_eq = False
    bot.send_message(message.chat.id, "После следующего события вы перестанеет отслеживать землетрясения!")


@bot.message_handler(content_types="text")
def func_allocator(message):
    # Функция обрабатывающая нажатия кнопок и в зависимости от текста, вызывает нужную функцию. Так и называеться, "распределитель функций"
    match message.text:
        case "📍 Установить местоположение":
            setplace(message)
        case "⭕ Установить радиус поиска":
            setradius(message)
        case "🌎 Найти землетрясения":
            fetch(message)
        case "ℹ️ Информация о проекте":
            info(message)
        case "🔎 Отслеживать землетрясения":
            track(message)
        case "❌ Не отслеживать землетрясения":
            untrack(message)
        case _:
            bot.send_message(message.chat.id, "Не найдено такой команды!")


def bot_loop():
    # Главный цикл бота
    try:
        bot.polling(none_stop=True)
    except:
        print("Ошибка подключения была подавлена")
        bot.polling(none_stop=True)


if __name__ == "__main__":
    bot_loop()