import os
import helpers
from flask import jsonify, render_template
from gevent.pywsgi import WSGIServer
from dotenv import load_dotenv
from flask_assets import Environment, Bundle
from bot import Bot
import logging
from threading import Thread
import asyncio
from config import application, db  # Импорт из config.py
import json
from models import Channel


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# Настройка логирования
logger = logging.getLogger('config')
logger.info("Starting server and bot")

env_value = os.getenv("UID7TV")
items = env_value.split(",") if env_value else []
UID7TV = {}
for item in items:
    parts = item.split("=")
    if len(parts) == 2:
        key = parts[0].strip().lower()
        value = parts[1].strip().lower()
        UID7TV[key] = value
CHANNELS = os.getenv('CHANNELS').split(',')
CHANNELS = [channel.strip().lower() for channel in CHANNELS]

assets = Environment(application)
assets.register('main_css', Bundle('styles/main.css', output='gen/main.css'))
assets.register('main_js', Bundle('scripts/main.js', output='gen/main.js'))
assets.register('index_js', Bundle('scripts/main.js', output='gen/main.js'))
assets.register('emotes_js', Bundle('scripts/main.js', output='gen/main.js'))

@application.route('/')
def index():
    return render_template('index.html', avatars = helpers.get_avatars())

@application.route('/channels', methods=['GET'])
def get_channels():
    return CHANNELS

@application.route('/<channel_name>')
def get_channel(channel_name):
    if channel_name in CHANNELS:
        return render_template('channel.html', channel_name=channel_name, channels=CHANNELS)
    else:
        return "Чат не найден", 404

@application.route('/<channel_name>/emotes', methods=['GET'])
async def get_emotes_by_channel(channel_name):
    if channel_name in CHANNELS:
        try:
            emotes = await helpers.get_emotes(helpers.UID7TV[channel_name])
            return jsonify(emotes)  # Возвращаем список словарей
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return "Emotes не найдены", 404

@application.route('/api/<channel_name>/stats')
def get_channel_stats(channel_name):
    try:
        with application.app_context():
            channel = Channel.query.filter_by(name=channel_name).first()
            if not channel:
                return jsonify({"error": "Channel not found"}), 404
            
            stats = {emote.name: emote.count for emote in channel.emotes}
            return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def run_flask():
    try:
        logger.info("Starting Flask server...")
        print("Starting Flask server...")
        http_server = WSGIServer(('0.0.0.0', 5000), application)
        http_server.serve_forever()
    except Exception as e:
        logger.error(f"Error running Flask server: {e}")
        print(f"Error running Flask server: {e}")

def run_bot():
    try:
        logger.info("Starting bot...")
        print("Starting bot...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        bot = Bot()
        bot.application = application  # Передаем приложение в бота
        bot.run()
    except Exception as e:
        logger.error(f"Error running bot: {e}")
        print(f"Error running bot: {e}")

# Убедитесь, что код запуска бота работает правильно
def start_bot_thread():
    try:
        logger.info("Starting bot thread...")
        print("Starting bot thread...")
        bot_thread = Thread(target=run_bot)
        bot_thread.daemon = True  # Позволяет завершить поток при завершении основного процесса
        bot_thread.start()
    except Exception as e:
        logger.error(f"Error starting bot thread: {e}")
        print(f"Error starting bot thread: {e}")

# Запуск функции для старта бота
start_bot_thread()
if __name__ == '__main__':
    # Запускаем Flask-сервер в основном потоке
    run_flask()
