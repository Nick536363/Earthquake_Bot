from telebot import TeleBot, types
from dotenv import load_dotenv, find_dotenv
from os import environ


load_dotenv(find_dotenv())
telegram_bot_token = environ["TELEGRAM_API"]
bot = TeleBot(telegram_bot_token)

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

def bot_loop():
    bot.polling(none_stop=True)


if __name__ == "__main__":
    bot_loop()