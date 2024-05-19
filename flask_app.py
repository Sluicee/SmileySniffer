# flask_app.py

import os
import helpers
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from flask_assets import Environment, Bundle
from bot import bot

# Получение значений переменных из файла .env
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    
UID7TV = dict(item.split("=") for item in os.getenv("UID7TV").split(","))
CHANNELS = os.getenv('CHANNELS').split(',')

app = Flask(__name__)  # Создание объекта приложения Flask
app.config['ASSETS_DEBUG'] = True

assets = Environment(app)

# Определение бандлов стилей и скриптов
assets.register('main_css', Bundle('styles/main.css', output='gen/main.css'))
assets.register('main_js', Bundle('scripts/main.js', output='gen/main.js'))

# Маршруты Flask
@app.route('/')
def index():
    return render_template('index.html')  # Отображение главной страницы

@app.route('/<channel_name>')
def get_channel(channel_name):
    if channel_name in CHANNELS:
        return render_template('channel.html', channel_name=channel_name)  # Отображение страницы канала
    else:
        return "Чат не найден", 404  # Вывод сообщения об ошибке 404

@app.route('/<channel_name>/messages', methods=['GET'])
def get_messages_by_channel(channel_name):
    if channel_name in CHANNELS:
        data = jsonify(list(filter(lambda person: person['channel'] == channel_name, bot.messages)))  # Фильтрация сообщений по каналу
        return data
    else:
        return "Чат не найден", 404  # Вывод сообщения об ошибке 404

@app.route('/<channel_name>/emotes', methods=['GET'])
def get_emotes_by_channel(channel_name):
    if channel_name in CHANNELS:
        data = jsonify(list(helpers.get_emotes(UID7TV[channel_name])))  # Получение смайликов для канала
        return data
    else:
        return "Emotes не найдены", 404  # Вывод сообщения об ошибке 404

@app.route('/send', methods=['POST'])
def send_message():
    data = request.json
    channel = data.get('channel')
    message = data.get('message')
    if channel and message:
        bot.loop.create_task(bot.send_message(channel, message))  # Отправка сообщения в чат
        return jsonify({'status': 'Message sent'})  # Вывод сообщения об успешной отправке
    return jsonify({'status': 'Failed to send message'}), 400  # Вывод сообщения об ошибке отправки сообщения
