import os
from datetime import date
from dotenv import load_dotenv, find_dotenv
from os import environ
import telebot


def find_last_earthquakes(place: str, days_ago=1):
    load_dotenv(find_dotenv())
    yandex_api_key = environ["YANDEX_API"]
    longitude, latitude = get_coords(place, apikey=yandex_api_key)
    if not latitude or not longitude:
        return None
    last_earthquakes = get_earthquakes(f"{date.today().year}-{date.today().month}-{date.today().day-days_ago}", date.today(), latitude, longitude)
    return last_earthquakes

bot = telebot.TeleBot(os.environ["тг токен"])

@bot.message_handler(commands=['earthquakes'])
def handle_earthquakes(message):
    try:
        place = message.text.split('/earthquakes ')[1]
        earthquakes = find_last_earthquakes(place)

        for quake in earthquakes:
            msg = f"""
🌍 {quake['title']}
📍 Место: {quake['place']}
📅 Дата: {quake['date']}
"""
            bot.send_message(message.chat.id, msg)
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {str(e)}")

bot.polling() 
