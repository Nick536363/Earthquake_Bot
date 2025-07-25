user_data = {}

@bot.message_handler(commands=['start'])
def handle_start(message):
    help_text = """
 *Бот для отслеживания землетрясений* 

/set_location - Установить ваше местоположение
/set_radius - Установить радиус поиска (по умолчанию 3000 км)
/last - Получить последние землетрясения
/track - Включить/выключить уведомления о новых землетрясениях
/help - Показать это сообщение

Сначала установите ваше местоположение
"""
    bot.send_message(message.chat.id, help_text, parse_mode="Markdown")

@bot.message_handler(commands=['help'])
def handle_help(message):
    handle_start(message)

@bot.message_handler(commands=['set_location'])
def handle_set_location(message):
    msg = bot.send_message(message.chat.id, "Введите название вашего города или местоположения:")
    bot.register_next_step_handler(msg, get_users_coords)

def get_users_coords(message):
    chat_id = message.chat.id
    place = message.text
    longitude, latitude = get_coords(place, YANDEX_API_KEY)
    if longitude is None or latitude is None:
        bot.send_message(chat_id, "Не найдено!\nУстановлены координаты по умолчанию (0, 0)")
        longitude, latitude = 0, 0
    else:
        bot.send_message(chat_id, f"Координаты установлены.\n{latitude} (широта), {longitude} (долгота)")
    user_data[chat_id] = user_data.get(chat_id, {})
    user_data[chat_id]['latitude'] = latitude
    user_data[chat_id]['longitude'] = longitude

@bot.message_handler(commands=['set_radius'])
def handle_set_radius(message):
    msg = bot.send_message(message.chat.id, " Введите радиус поиска в км (макс. 20000):")
    bot.register_next_step_handler(msg, get_search_radius)

def get_search_radius(message):
    chat_id = message.chat.id
    argument = message.text.strip()
    if not argument.isdigit():
        bot.send_message(chat_id, "Укажите число!")
        return
    radius = int(argument)
    if radius < 1 or radius > 20000:
        bot.send_message(chat_id, "Радиус от 1 до 20 000 км.")
        return
    user_data[chat_id] = user_data.get(chat_id, {})
    user_data[chat_id]['radius'] = radius
    bot.send_message(chat_id, f"Радиус поиска установлен на значение {radius} км.")

@bot.message_handler(commands=['last'])
def handle_last_earthquakes(message):
    msg = bot.send_message(message.chat.id, " За сколько последних дней показать землетрясения? (1-30):")
    bot.register_next_step_handler(msg, get_last_earthquakes)

def get_last_earthquakes(message):
    chat_id = message.chat.id
    argument = message.text.strip()
    if not argument.isdigit():
        bot.send_message(chat_id, "Вы должны указать число!")
        return
    days = int(argument)
    if days < 1 or days > 30:
        bot.send_message(chat_id, "Можно указать только от 1 до 30 дней!")
        return
    data = user_data.get(chat_id, {})
    latitude = data.get('latitude', 0)
    longitude = data.get('longitude', 0)
    radius = data.get('radius', 3000)
    earthquakes = find_last_earthquakes(latitude, longitude, days, radius)
    if not earthquakes:
        bot.send_message(chat_id, "Не было найдено землетрясений")
        return
    bot.send_message(chat_id, "Ниже приведен список найденных землетрясений:")
    for earthquake in earthquakes:
        send_eq_data(message, earthquake)

@bot.message_handler(commands=['track'])
def handle_track(message):
    chat_id = message.chat.id
    data = user_data.get(chat_id, {})
    tracking_new_eq = not data.get('tracking_new_eq', False)
    user_data[chat_id] = data
    user_data[chat_id]['tracking_new_eq'] = tracking_new_eq
    status = "включены" if tracking_new_eq else "выключены"
    bot.send_message(chat_id, f" Уведомления о новых землетрясениях {status}!")
    if tracking_new_eq:
        bot.send_message(chat_id, " Начинаю отслеживание новых землетрясений...")
        latitude = data.get('latitude', 0)
        longitude = data.get('longitude', 0)
        radius = data.get('radius', 3000)
        track_new_earthquakes(bot, chat_id, latitude, longitude, radius)

@bot.message_handler(func=lambda message: True)
def handle_unknown(message):
    bot.send_message(message.chat.id, "не понимаю эту команду. Введите /help для списка команд")

if __name__ == "__main__":
    print("бот запущен")
    bot.infinity_polling()
