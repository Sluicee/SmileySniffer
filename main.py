# main.py
# -*- coding: utf-8 -*-

import os
import helpers
from dotenv import load_dotenv
from flask_app import application
#from gevent.pywsgi import WSGIServer
from helpers import get_emotes
import logging
from bot import Bot

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

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
    
logging.basicConfig(level=logging.INFO, filename="logs/py_log.log",filemode="w",encoding = 'utf-8',
                    format="%(asctime)s %(levelname)s %(message)s")
logging.info("logger")
logger = logging.getLogger('main')

# bot = Bot()

# if __name__ == '__main__':
#     import threading
#     bot_thread = threading.Thread(target=bot.run)  # Создание потока для запуска бота
#     bot_thread.start()  # Запуск потока
#     application.run(host='0.0.0.0', port=5000, debug=True)  # Запуск приложения Flask
#     # http_server = WSGIServer(('0.0.0.0', 5000), application)
#     # http_server.serve_forever()