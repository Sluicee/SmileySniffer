import os  # Импорт модуля для работы с операционной системой
import requests  # Импорт модуля для отправки HTTP-запросов
import json  # Импорт модуля для работы с JSON данными
from twitchio.ext import commands  # Импорт класса для создания бота на Twitch
from flask import Flask, request, jsonify, render_template  # Импорт Flask и связанных модулей
from dotenv import load_dotenv  # Импорт функции для загрузки переменных из файла .env
from flask_assets import Environment, Bundle

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
API_URL_7TV = 'https://7tv.io/v3'
USERS_7TV_API = '/users/'
EMOTESETS_7TV_API = '/emote-sets/'
UID7TV = dict(item.split("=") for item in os.getenv("UID7TV").split(","))

# Класс для создания Twitch-бота
class Bot(commands.Bot):
    
    def __init__(self):
        super().__init__(token=OAUTH_TOKEN, prefix=PREFIX, initial_channels=CHANNELS)
        self.messages = []  # Список для хранения сообщений

    async def event_ready(self):
        print(f'Logged in as | {self.nick}')  # Вывод информации о входе в аккаунт
        print(f'User id is | {self.user_id}')  # Вывод id пользователя

    async def event_message(self, message):
        if message.echo:  # Проверка на наличие эхо
            return
        
        # Сохранение сообщений в список
        self.messages.append({
            'channel' : message.channel.name,
            'author': message.author.name,
            'content': message.content
        })

        print(f'{message.author.name}: {message.content}')  # Вывод сообщений в консоль
        await self.handle_commands(message)
        
    @commands.command(name='emotes')
    async def emotes(self, ctx, *, username: str = ''):
        await ctx.send(f'xdd')  # Отправка сообщения в чат

    async def send_message(self, channel, message):
        await self.get_channel(channel).send(message)  # Отправка сообщения в чат

# Функция для получения id набора смайликов пользователя из 7TV API
def get_7tv_user_emote_set_id(channel_id):
    url = API_URL_7TV + USERS_7TV_API + channel_id
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Error: {response.status_code}')
        return []

# Функция для получения списка смайликов из 7TV API
def get_7tv_emotes(channel_id):
    emote_set = get_7tv_user_emote_set_id(channel_id)["emote_sets"][0]['id']
    url = API_URL_7TV + EMOTESETS_7TV_API + emote_set
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Error: {response.status_code}')
        return []

# Функция для получения смайликов из 7TV API
def get_emotes(channel_id):
    emotes = get_7tv_emotes(channel_id)['emotes']
    if emotes:
        return emotes
    else:
        print('No emotes found')

# Создание объекта бота
bot = Bot()
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
        data = jsonify(list(get_emotes(UID7TV[channel_name])))  # Получение смайликов для канала
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

if __name__ == '__main__':
    import threading
    bot_thread = threading.Thread(target=bot.run)  # Создание потока для запуска бота
    bot_thread.start()  # Запуск потока
    app.run(host='0.0.0.0', port=5000)  # Запуск приложения Flask
    
