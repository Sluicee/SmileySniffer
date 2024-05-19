# main.py

import os
from dotenv import load_dotenv
from bot import bot
from flask_app import app
from helpers import get_emotes

# Загрузка переменных из файла .env
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# Получение значений переменных из файла .env
OAUTH_TOKEN = os.getenv('OAUTH_TOKEN')
REFRESH_TOKEN = os.getenv('REFRESH_TOKEN')
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
PREFIX = os.getenv('PREFIX')
CHANNELS = os.getenv('CHANNELS').split(',')
UID7TV = dict(item.split("=") for item in os.getenv("UID7TV").split(","))


if __name__ == '__main__':
    import threading
    bot_thread = threading.Thread(target=bot.run)  # Создание потока для запуска бота
    bot_thread.start()  # Запуск потока
    app.run(host='0.0.0.0', port=5000)  # Запуск приложения Flask
