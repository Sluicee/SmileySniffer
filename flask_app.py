import os
import helpers
from quart import Quart, jsonify, render_template
from dotenv import load_dotenv
from bot import Bot
import json
import logging
from threading import Thread
import asyncio

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# Настройка логирования
try:
    if not os.path.exists('logs'):
        os.makedirs('logs')
    logging.basicConfig(level=logging.INFO, filename="logs/py_log.log", filemode="w", encoding='utf-8',
                        format="%(asctime)s %(levelname)s %(message)s")
    logger = logging.getLogger('flask_app')
    logger.info("Starting server and bot")
except Exception as e:
    print(f"Failed to set up logging: {e}")
    raise

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
DATA_DIR = os.getenv('DATA_DIR')

application = Quart(__name__, static_folder='static')
application.config['ASSETS_DEBUG'] = True
application.debug = True


@application.route('/')
async def index():
    return await render_template('index.html')


@application.route('/channels', methods=['GET'])
async def get_channels():
    return jsonify(CHANNELS)


@application.route('/<channel_name>')
async def get_channel(channel_name):
    if channel_name in CHANNELS:
        return await render_template('channel.html', channel_name=channel_name, channels=CHANNELS)
    else:
        return "Чат не найден", 404


@application.route('/<channel_name>/emotes', methods=['GET'])
async def get_emotes_by_channel(channel_name):
    if channel_name in UID7TV:
        emotes = await helpers.get_emotes(UID7TV[channel_name])
        return jsonify(list(emotes))
    else:
        return "Emotes не найдены", 404


@application.route('/download/<channel>.json', methods=['GET'])
async def download_json(channel):
    channel_file_path = os.path.join(DATA_DIR, f'{channel}.json')

    if os.path.exists(channel_file_path):
        try:
            with open(channel_file_path, 'r') as file:
                data = json.load(file)
            return jsonify(data)
        except Exception as e:
            return jsonify({'status': 'Failed to send file', 'error': str(e)}), 500
    else:
        return jsonify({'status': 'File not found'}), 404


def run_bot():
    try:
        logger.info("Starting bot...")
        print("Starting bot...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        bot = Bot()
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
    try:
        from hypercorn.asyncio import serve

        logger.info("Starting Quart server...")
        print("Starting Quart server...")
        loop = asyncio.get_event_loop()
        loop.create_task(application.run_task(host='0.0.0.0', port=5000))
        loop.run_forever()
    except Exception as e:
        logger.error(f"Error running Quart server: {e}")
        print(f"Error running Quart server: {e}")

