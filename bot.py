import os
import helpers
import json
from dotenv import load_dotenv
from twitchio.ext import commands
import time
import schedule

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

OAUTH_TOKEN = os.getenv('OAUTH_TOKEN')
PREFIX = os.getenv('PREFIX')
CHANNELS = os.getenv('CHANNELS').split(',')
UID7TV = dict(item.split("=") for item in os.getenv("UID7TV").split(","))
DATA_DIR = os.getenv('DATA_DIR')

class Bot(commands.Bot):
    
    def __init__(self):
        super().__init__(token=OAUTH_TOKEN, prefix=PREFIX, initial_channels=CHANNELS)
        self.messages = []  # Список для хранения сообщений
        self.emotes = self.load_emotes()
        schedule.every(1).minute.do(self.load_emotes)  # Выполняем функцию load_emotes каждую минуту

    async def event_ready(self):
        print(f'Logged in as | {self.nick}')  # Вывод информации о входе в аккаунт
        print(f'User id is | {self.user_id}')  # Вывод id пользователя

    async def event_message(self, message):
        if message.echo:  # Проверка на наличие эхо
            return
        
        # Сохранение сообщений в список с временной меткой
        self.messages.append({
            'channel': message.channel.name,
            'author': message.author.name,
            'content': message.content,
            'timestamp': time.time()  # Добавим временную метку
        })

        print(f'{message.author.name}: {message.content}')  # Вывод сообщений в консоль
        
        if "@SmileySniffer привет" == message.content:
            await self.echo_msg(message.channel.name, "привет :)")
        
        for word in message.content.split():
            if word in self.emotes[CHANNELS.index(message.channel.name)]:
                await self.save_word(message.channel.name, word)
        
        await self.handle_commands(message)
        
    @commands.command(name='emotes')
    async def emotes(self, ctx, *, username: str = ''):
        await ctx.send(f'xdd')  # Отправка сообщения в чат
        
    async def send_message(self, channel, message):
        channel_obj = self.get_channel(channel)
        if channel_obj:
            await channel_obj.send(message)  # Отправка сообщения в чат
        else:
            print(f"Channel {channel} not found.")
            
    @helpers.cooldown(7.5)
    async def echo_msg(self, channel, message):
        channel_obj = self.get_channel(channel)
        if channel_obj:
            await channel_obj.send(message)  # Отправка сообщения в чат
        else:
            print(f"Channel {channel} not found.")
    
    def load_emotes(self):
        emotes_array = []  # Создаем пустой двумерный массив для хранения смайликов по каналам
        for channel in UID7TV:
            emotes_for_channel = []  # Создаем пустой список для смайликов конкретного канала
            
            # Получаем смайлики для текущего канала
            channel_emotes = helpers.get_emote_names(helpers.get_emotes(UID7TV[channel]))
            
            # Добавляем смайлики в список emotes_for_channel
            emotes_for_channel.extend(channel_emotes)
            
            # Добавляем список смайликов текущего канала в двумерный массив
            emotes_array.append(emotes_for_channel)
        print("Emotes reloaded")
        return emotes_array
        
    async def save_word(self, channel, word):  # Добавляем метод save_word
        try:
            # Создаем имя JSON файла для данного канала
            channel_filename = f'{channel}.json'
            channel_file_path = os.path.join(DATA_DIR, channel_filename)
            
            # Создаем или обновляем JSON файл
            if os.path.exists(channel_file_path):
                with open(channel_file_path, 'r+') as file:
                    data = json.load(file)
                    data[word] = data.get(word, 0) + 1
                    file.seek(0)
                    json.dump(data, file, indent=4)
            else:
                with open(channel_file_path, 'w') as file:
                    json.dump({word: 1}, file, indent=4)
            
            print('Word saved successfully')
        except Exception as e:
            print('Error saving word:', str(e))

bot = Bot()
