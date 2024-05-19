# bot.py

import os
import helpers
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
FAVS = ["widetime","Taah","cannyCat","1984",")))","well","dobro","sdd","PogT","ABOBA","TaaPls","WideCatGroove"]
FAV_PHRASES = ["MyHonestReaction TeaTime","Bedge TeaTime","docnotL ботоводы блять"]
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
        
        if "Taa" in message.content.split():
            await self.send_message(message.channel.name, "Нет курению Taa")
            
        # Проверка наличия элементов и вывод первого совпавшего
        for word in message.content.split():
            if word in FAVS:
                await self.send_message(message.channel.name, word)
                print("Слово найдено в строке.")
                break
        else:
            print("Ни один из элементов не найден")
            
        for phrase in FAV_PHRASES:
            if phrase in message.content:
                await self.send_message(message.channel.name, phrase)
                print("Фраза найдена в строке.")
                break
        else:
            print("Ни одна из фраз не найдена")
        await self.handle_commands(message)
        
    @commands.command(name='emotes')
    async def emotes(self, ctx, *, username: str = ''):
        await ctx.send(f'xdd')  # Отправка сообщения в чат
        
    @helpers.cooldown(2.5)
    async def send_message(self, channel, message):
        channel_obj = self.get_channel(channel)
        if channel_obj:
            await channel_obj.send(message)  # Отправка сообщения в чат
        else:
            print(f"Channel {channel} not found.")

bot = Bot()
