import os
import helpers
import json
from dotenv import load_dotenv
from twitchio.ext import commands
import time
import logging
import tempfile
import re
import asyncio

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    
OAUTH_TOKEN = os.getenv('OAUTH_TOKEN')
PREFIX = os.getenv('PREFIX')
CHANNELS = os.getenv('CHANNELS').split(',')
CHANNELS = [channel.strip().lower() for channel in CHANNELS]
env_value = os.getenv("UID7TV")
items = env_value.split(",") if env_value else []
UID7TV = {}
for item in items:
    parts = item.split("=")
    if len(parts) == 2:
        key = parts[0].strip().lower()
        value = parts[1].strip().lower()
        UID7TV[key] = value
DATA_DIR = os.getenv('DATA_DIR')

logger = logging.getLogger('flask_app')

class Bot(commands.Bot):
    
    def __init__(self):
        super().__init__(token=OAUTH_TOKEN, prefix=PREFIX, initial_channels=CHANNELS)
        self.messages = []  # Список для хранения сообщений
        self.emotes = [[] for _ in CHANNELS]
        logger.info("BOT init")

    async def event_ready(self):
        logger.info(f'Logged in as | {self.nick}')  # Вывод информации о входе в аккаунт
        print(f'Logged in as | {self.nick}')  # Вывод информации о входе в аккаунт
        logger.info(f'User id is | {self.user_id}')  # Вывод id пользователя
        print(f'User id is | {self.user_id}')  # Вывод id пользователя
        self.emotes = await helpers.load_emotes()
        self.loop.create_task(self.schedule_load_emotes())

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

        logger.debug(f'{message.author.name}: {message.content}')  # Вывод сообщений в консоль
        #print(f'{message.author.name}: {message.content}')  # Вывод сообщений в консоль
        
        if "@SmileySniffer привет" == message.content:
            await self.echo_msg(message.channel.name, "привет :)")
        
        for word in message.content.split():
            if word in self.emotes[CHANNELS.index(message.channel.name)]:
                await self.save_word(message.channel.name, word)
        
        await self.handle_commands(message)
        
    @commands.cooldown(rate=1, per=15, bucket=commands.Bucket.channel)
    @commands.command(name='emote')
    async def fetch_emotes_command(self, ctx: commands.Context, emote_name: str):
        if emote_name == "uzyAnalProlapse":
            await ctx.channel.send(f'uzyAnalProlapse использован *ДАННЫЕ УДАЛЕНЫ* раз, Ранг: *ДАННЫЕ УДАЛЕНЫ*')
            return
        try:
            # Попытка получить имя канала через ctx.channel.name
            channel_name = ctx.channel.name
            channel_filename = f'{channel_name}.json'
            channel_file_path = os.path.join(DATA_DIR, channel_filename)

            if os.path.exists(channel_file_path):
                with open(channel_file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)

                # Сортируем смайлики по количеству использований в убывающем порядке
                sorted_emotes = sorted(data.items(), key=lambda item: item[1], reverse=True)
                
                # Поиск ранга смайлика
                emote_rank = next((rank for rank, (name, _) in enumerate(sorted_emotes, start=1) if name == emote_name), None)

                if emote_name in data:
                    emote_value = data[emote_name]
                    times_word = helpers.get_times_word(emote_value)
                    if emote_rank is not None:
                        await ctx.channel.send(f'{emote_name} использован {emote_value} {times_word}, Ранг: {emote_rank}')
                    else:
                        await ctx.channel.send(f'{emote_name} использован {emote_value} {times_word}')
                else:
                    return
                    # await ctx.channel.send(f'{emote_name} не найден')
            else:
                await ctx.channel.send(f'Канал "{channel_name}" не найден.')

        except Exception as e:
            await ctx.channel.send(f'Произошла ошибка: {str(e)}')
    
    @commands.cooldown(rate=1, per=15, bucket=commands.Bucket.channel)
    @commands.command(name='top')
    async def top(self, ctx: commands.Context):
        await ctx.channel.send(f'Топ смайликов 7TV: https://emotes.sluicee.space/{ctx.channel.name}')
     
    async def send_message(self, channel, message):
        channel_obj = self.get_channel(channel)
        if channel_obj:
            await channel_obj.send(message)  # Отправка сообщения в чат
        else:
            logger.error(f"Channel {channel} not found.")
            print(f"Channel {channel} not found.")
            
    @helpers.cooldown(7.5)
    async def echo_msg(self, channel, message):
        channel_obj = self.get_channel(channel)
        if channel_obj:
            await channel_obj.send(message)  # Отправка сообщения в чат
        else:
            logger.error(f"Channel {channel} not found.")
            print(f"Channel {channel} not found.")
    
    async def load_emotes_task(self):
        self.emotes = await helpers.load_emotes()
        
    async def schedule_load_emotes(self):
        while True:
            await asyncio.sleep(300)  # Подождать 300 секунд перед вызовом
            self.emotes = asyncio.create_task(self.load_emotes_task())
    
    async def save_word(self, channel, word):  # Добавляем метод save_word
        try:
            # Создаем имя JSON файла для данного канала
            channel_filename = f'{channel}.json'
            channel_file_path = os.path.join(DATA_DIR, channel_filename)
            
            # Загружаем данные из существующего файла, если он существует
            data = {}
            if os.path.exists(channel_file_path):
                with open(channel_file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
            
            # Обновляем данные
            data[word] = data.get(word, 0) + 1

            # Записываем обновленные данные во временный файл
            temp_file_path = None
            try:
                dir_name = os.path.dirname(channel_file_path)
                with tempfile.NamedTemporaryFile('w', delete=False, dir=dir_name, suffix='.tmp', encoding='utf-8') as temp_file:
                    temp_file_path = temp_file.name
                    json.dump(data, temp_file, indent=4)
            
                # После успешной записи во временный файл, заменяем основной файл
                os.replace(temp_file_path, channel_file_path)
                logger.debug('Word saved successfully')
                print('Word saved successfully')
            except Exception as e:
                if temp_file_path and os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                raise e

        except Exception as e:
            logger.error('Error saving word: %s', str(e))
            print('Error saving word:', str(e))

