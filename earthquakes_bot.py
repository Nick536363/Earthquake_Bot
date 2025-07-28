from telebot import TeleBot, types
from dotenv import load_dotenv, find_dotenv
from os import environ
from earthquakes_info import find_last_earthquakes, track_new_earthquakes, get_coords
from time import sleep


load_dotenv(find_dotenv())
telegram_bot_token = environ["TELEGRAM_API"]
yandex_api_key = environ["YANDEX_API"]
bot = TeleBot(telegram_bot_token)
longitude, latitude = 0, 0
radius = 3000
users_settings = {}


def send_eq_data(message, earthquake: dict):
    # Отправка сообщения с данными о землетрясении
    chat_id = message.chat.id
    markup = types.InlineKeyboardMarkup(row_width=1)
    map_button = types.InlineKeyboardButton(text="🗺 Карта события", url = earthquake["map"])
    region_button = types.InlineKeyboardButton(text="🧭 Региональная информация", url = earthquake["region-info"])
    markup.add(map_button, region_button)
    bot.send_message(chat_id, f"""
📝 {earthquake["title"]}

🚩 Место события -> {earthquake["place"]}
🕘 Время события по UTC -> {earthquake["date"]}
↔️ Расстояние до пользователя ->  {earthquake["distance"]} км

🌐↔️ Географическая широта -> {earthquake["latitude"]}
🌐↕ Географическая долгота -> {earthquake["longitude"]}
                """, reply_markup=markup)


def get_users_coords(message):
    # Установка координат с помощью функции из earthquakes_info.py
    global users_settings
    chat_id = message.chat.id
    place = message.text
    users_settings[chat_id]["longitude"], users_settings[chat_id]["latitude"] = get_coords(place, yandex_api_key)
    users_settings[chat_id]["place"] = place
    if not users_settings[chat_id]["longitude"] or not users_settings[chat_id]["latitude"]:
        bot.send_message(chat_id, "Место не было найдено!\nУстановлены координаты по умолчанию (0, 0)")
        users_settings[chat_id]["longitude"], users_settings[chat_id]["latitude"] = 0, 0
        return None
    bot.send_message(chat_id, f"Координаты успешно установлены!\n{users_settings[chat_id]["latitude"]} (широта), {users_settings[chat_id]["longitude"]} (долгота)")


def get_search_radius(message):
    # Установка значения максимального радиуса
    global users_settings
    chat_id = message.chat.id
    argument = message.text
    if len(argument.split()) > 1:
        bot.send_message(chat_id, "Вы должны указать только одно число!")
        return None
    elif not argument.isdigit():
        bot.send_message(chat_id, "Вы должны указать число!")
        return None
    elif int(argument) > 20001 or int(argument) < 1:
        bot.send_message(chat_id, "Радиус должен быть в диапазоне от 1 до 20.001 км!")
        return None
    users_settings[chat_id]["radius"] = int(argument)
    bot.send_message(chat_id, f"Радиус поиска установлен на значение {int(argument)} км.")


def get_last_earthquakes(message):
    # Отправка пользователю землетрясений за последние N дней
    global users_settings
    chat_id = message.chat.id
    sending_delay = 1
    argument = message.text
    if len(argument.split()) > 1:
        bot.send_message(chat_id, "Вы должны указать только одно число!")
        return None
    elif not argument.isdigit():
        bot.send_message(chat_id, "Вы должны указать число!")
        return None
    elif int(argument) < 1 or int(argument) > 27:
        bot.send_message(chat_id, "Вы должны указать число в диапазоне от 1 до 27!")
        return None

    earthquakes = find_last_earthquakes(users_settings[chat_id]["latitude"], users_settings[chat_id]["longitude"], int(argument), users_settings[chat_id]["radius"])

    if not len(earthquakes):
        bot.send_message(chat_id, "Не было найдено землетрясений по критериям пользователя")
        return None

    bot.send_message(chat_id, "Ниже приведен список найденных землетрясений:")
    for earthquake in earthquakes:
        send_eq_data(message, earthquake)
        sleep(sending_delay)


# Далее в основном идут функции-обработчики. Это значит что дальше в основном будут "триггеры" на команды пользователя, которые вызывают функции приведенные выше.
# Но также будут и функции-обработчики, которые не вызывают других функций, а делают всё "сами"


@bot.message_handler(commands=["start", "help"])
def start(message):
    # Функция показывающая все доступные команды и отрисовывающая кнопки
    global users_settings
    chat_id = message.chat.id
    users_settings[chat_id] = {"tracking": False,
    "latitude": 0,
    "longitude": 0,
    "radius": 3000,
    "place": "Остров Ноль"
    }
    markup = types.ReplyKeyboardMarkup()
    setplace_button = types.KeyboardButton("📍 Установить местоположение") 
    setradius_button = types.KeyboardButton("⭕ Установить радиус поиска")
    fetch_button = types.KeyboardButton("🌎 Найти землетрясения")
    info_button = types.KeyboardButton("ℹ️ Информация о проекте")
    settings_button = types.KeyboardButton("⚙️ Конфигурация")
    track_button = types.KeyboardButton("🔎 Отслеживать землетрясения")
    untrack_button = types.KeyboardButton("❌ Не отслеживать землетрясения")
    markup.add(setplace_button, setradius_button, fetch_button, track_button, untrack_button, info_button, settings_button)
    bot.send_message(chat_id, """
    Список доступных комманд:

/setplace -> установить своё местоположение (по умолчанию Остров Ноль)
/setradius -> установить радиус в километрах поиска землетрясений (по умолчанию 3000)
/fetch -> получить землетрясения за последнее время
/track -> отслеживать новые землетрясения
/untrack -> перестать отслеживать новые землетрясения
/settings -> вывод текующей конфигурации
/info -> информация о проекте
/help либо /start -> вывод данного сообщения
    """, reply_markup=markup)


@bot.message_handler(commands=["info"])
def info(message):
    # Функция показывающая информацию о проекте
    chat_id = message.chat.id
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text="📩 Ссылка на репозиторий", url = "https://github.com/Nick536363/Earthquake_Bot")
    markup.add(button)
    bot.send_message(chat_id, """
    Информация о проекте:

Ведущий программист: Nick536363
    """, reply_markup=markup)


@bot.message_handler(commands=["settings"])
def settings(message):
    #  Функция для вывода конфигурации пользователя
    global users_settings
    chat_id = message.chat.id
    bot.send_message(chat_id, f"""
    Текущая конфигурация:

Местоположение пользователя -> {users_settings[chat_id]["place"]}
Радиус поиска -> {users_settings[chat_id]["radius"]}
Отслеживаються ли новые землетрясения -> {"Да" if users_settings[chat_id]["tracking"] else "Нет"}
Географическая широта пользователя -> {users_settings[chat_id]["latitude"]}
Географическая долгота пользователя -> {users_settings[chat_id]["longitude"]}

    """)


@bot.message_handler(commands=["setplace"])
def setplace(message):
    # Функция для получения названия населенного пункта от пользователя
    chat_id = message.chat.id
    bot.send_message(chat_id, "Пожалуйста, введите название своего населенного пункта (город, поселок, деревня и т.п.).")
    bot.register_next_step_handler(message, get_users_coords)
    

@bot.message_handler(commands=["setradius"])
def setradius(message):
    # Функция для получения максимального радиуса от пользователя
    chat_id = message.chat.id
    bot.send_message(chat_id, "Пожалуйста, введите радиус поиска землетрясения в километрах (20.001 максимально)")
    bot.register_next_step_handler(message, get_search_radius)


@bot.message_handler(commands=["fetch"])
def fetch(message):
    # Функция для получения значения от пользователя, за сколько последних дней искать землетрясения 
    chat_id = message.chat.id
    bot.send_message(chat_id, "Пожалуйста, укажите за сколько последних дней вы хотите найти землетрясения (максимально 27)")
    bot.register_next_step_handler(message, get_last_earthquakes)


@bot.message_handler(commands=["track"])
def track(message):
    # Функция для начала отслеживания землетрясений
    chat_id = message.chat.id
    global users_settings
    if chat_id in users_settings:
        if users_settings[chat_id]["tracking"]:
            bot.send_message(chat_id, "Вы уже отслеживаете новые землетрясения!")
            return None
    users_settings[chat_id]["tracking"] = True
    bot.send_message(chat_id, "Теперь новые землетрясения будут приходить Вам!")
    while users_settings[chat_id]["tracking"]:
        new_earthquakes = track_new_earthquakes(users_settings[chat_id]["latitude"], users_settings[chat_id]["longitude"], users_settings[chat_id]["radius"], users_settings[chat_id]["tracking"])
        bot.send_message(chat_id, "Новое событие!")
        for earthquake in new_earthquakes:
            send_eq_data(message, earthquake)


@bot.message_handler(commands=["untrack"])
def untrack(message):
    # Функция для заканчивания отслеживания землетрясений
    chat_id = message.chat.id
    global users_settings
    if chat_id in users_settings:
        if not users_settings[chat_id]["tracking"]:
            bot.send_message(chat_id, "Вы не новые землетрясения!")
            return None
        users_settings[chat_id]["tracking"] = False
    bot.send_message(chat_id, "После следующего события вы перестанеет отслеживать землетрясения!")


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
        case "⚙️ Конфигурация":
            settings(message)
        case _:
            bot.send_message(chat_id, "Не найдено такой команды!")


def bot_loop():
    # Главный цикл бота
    try:
        bot.polling(none_stop=True)
    except KeyboardInterrupt:
        exit()
    except:
        print("Ошибка была подавлена!")
        bot_loop()


if __name__ == "__main__":
    bot_loop()