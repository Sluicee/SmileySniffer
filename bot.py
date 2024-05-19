# bot.py

import os
from dotenv import load_dotenv
from twitchio.ext import commands

# Получение значений переменных из файла .env
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# Получение значений переменных из файла .env
OAUTH_TOKEN = os.getenv('OAUTH_TOKEN')
PREFIX = os.getenv('PREFIX')
CHANNELS = os.getenv('CHANNELS').split(',')
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

bot = Bot()
