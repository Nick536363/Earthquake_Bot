import os
from datetime import date
from dotenv import load_dotenv, find_dotenv
from os import environ
import telebot

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
