import os
from sqlalchemy import update
import helpers
from dotenv import load_dotenv
from twitchio.ext import commands
from typing import Optional
import time
import logging
import asyncio
from models import Channel, Emote  # Импорт из models.py
from config import application, db

# Загрузка переменных окружения из файла .env
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# Инициализация переменных окружения
OAUTH_TOKEN = os.getenv('OAUTH_TOKEN')
PREFIX = os.getenv('PREFIX')
CHANNELS = os.getenv('CHANNELS').split(',')
CHANNELS = [channel.strip().lower() for channel in CHANNELS]
env_value = os.getenv("UID7TV")
items = env_value.split(",") if env_value else []
UID7TV = {item.split("=")[0].strip().lower(): item.split("=")[1].strip().lower() for item in items if "=" in item}
TOP_COMMAND_MAX_LIST = int(os.getenv("TOP_COMMAND_MAX_LIST"))

logger = logging.getLogger('config')


class Bot(commands.Bot):

    def __init__(self):
        super().__init__(token=OAUTH_TOKEN, prefix=PREFIX, initial_channels=CHANNELS)
        self.application = application  # Сохраняем ссылку на приложение
        self.messages = []  # Список для хранения сообщений
        self.emotes = [[] for _ in CHANNELS]  # Список для хранения эмодзи для каждого канала
        logger.info("BOT init")

    async def event_ready(self):
        """Вызывается при успешном подключении бота к Twitch."""
        logger.info(f'Logged in as | {self.nick}')  # Логгирование имени пользователя
        print(f'Logged in as | {self.nick}')  # Печать имени пользователя
        logger.info(f'User id is | {self.user_id}')  # Логгирование id пользователя
        print(f'User id is | {self.user_id}')  # Печать id пользователя
        self.emotes = await helpers.load_emotes()  # Загрузка эмодзи
        self.loop.create_task(self.schedule_load_emotes())  # Запуск задачи периодической загрузки эмодзи

    async def event_message(self, message):
        """Обрабатывает входящие сообщения."""
        if message.echo:  # Проверка на эхо-сообщение
            return

        # Сохранение сообщений в список с временной меткой
        self.messages.append({
            'channel': message.channel.name,
            'author': message.author.name,
            'content': message.content,
            'timestamp': time.time()  # Добавление временной метки
        })

        logger.debug(f'{message.author.name}: {message.content}')  # Логгирование сообщений

        if "@SmileySniffer привет" == message.content:
            await self.echo_msg(message.channel.name, "привет :)")  # Отправка приветственного сообщения

        # Проверка и сохранение слов, если они содержат эмодзи
        for word in message.content.split():
            if word in self.emotes[CHANNELS.index(message.channel.name)]:
                await self.save_word(message.channel.name, word)

        await self.handle_commands(message)  # Обработка команд

    async def get_channel_data(self, channel_name):
        # Используем переданное приложение
        with application.app_context():
            channel = Channel.query.filter_by(name=channel_name).first()
            if channel:
                return {emote.name: emote.count for emote in channel.emotes}
            return None

    async def send_channel_emotes(self, ctx, amount, order='desc'):
        """Отправка эмодзи канала в чат."""
        try:
            channel_name = ctx.channel.name
            data = await self.get_channel_data(channel_name)
            
            if data:
                emotes_list = list(data.items())
                sorted_emotes = sorted(emotes_list, key=lambda item: item[1], reverse=(order == 'desc'))
                selected_emotes = sorted_emotes[:amount]
                output = " ".join([f"{idx + 1}. {emote[0]} ({emote[1]})" for idx, emote in enumerate(selected_emotes)])
                await ctx.channel.send(f'{"Top" if order == "desc" else "Последние"} {amount}: {output}')
            else:
                await ctx.channel.send(f'Канал "{channel_name}" не найден.')

        except Exception as e:
            logger.error(f'Произошла ошибка: {str(e)}')
            await print(f'Произошла ошибка: {str(e)}')

    @commands.cooldown(rate=1, per=5, bucket=commands.Bucket.channel)
    @commands.command(name='emote')
    async def fetch_emotes_command(self, ctx: commands.Context, emote_name: str):
        """Команда для получения информации о конкретной эмодзи."""
        if emote_name == "uzyAnalProlapse":
            await ctx.channel.send(f'uzyAnalProlapse использован *ДАННЫЕ УДАЛЕНЫ* раз, Ранг: *ДАННЫЕ УДАЛЕНЫ*')
            return
        try:
            channel_name = ctx.channel.name
            data = await self.get_channel_data(channel_name)

            if data:
                sorted_emotes = sorted(data.items(), key=lambda item: item[1], reverse=True)
                emote_rank = next((rank for rank, (name, _) in enumerate(sorted_emotes, start=1) if name == emote_name), None)

                if emote_name in data:
                    emote_value = data[emote_name]
                    times_word = helpers.get_times_word(emote_value)
                    rank_message = f', Ранг: {emote_rank}' if emote_rank is not None else ''
                    await ctx.channel.send(f'{emote_name} использован {emote_value} {times_word}{rank_message}')
                else:
                    return
            else:
                await ctx.channel.send(f'Канал "{channel_name}" не найден.')

        except Exception as e:
            logger.error(f'Произошла ошибка: {str(e)}')
            await print(f'Произошла ошибка: {str(e)}')

    @commands.cooldown(rate=1, per=10, bucket=commands.Bucket.channel)
    @commands.command(name='top')
    async def top(self, ctx: commands.Context, amount: Optional[int]):
        """Команда для получения топа эмодзи."""
        if amount is None:
            await ctx.channel.send(f'Топ смайликов 7TV: https://emotes.sluicee.space/{ctx.channel.name} (SSL когда-нибудь куплю aga )')
        elif amount <= TOP_COMMAND_MAX_LIST:
            await self.send_channel_emotes(ctx, amount, order='desc')

    @commands.cooldown(rate=1, per=10, bucket=commands.Bucket.channel)
    @commands.command(name='last')
    async def latest(self, ctx: commands.Context, amount: Optional[int]):
        """Команда для получения последних использованных эмодзи."""
        if amount is None:
            await ctx.channel.send(f'Последние смайлики 7TV: https://emotes.sluicee.space/{ctx.channel.name} (SSL когда-нибудь куплю aga )')
        elif amount <= TOP_COMMAND_MAX_LIST:
            await self.send_channel_emotes(ctx, amount, order='asc')

    async def send_message(self, channel, message):
        """Отправка сообщения в канал."""
        channel_obj = self.get_channel(channel)
        if channel_obj:
            await channel_obj.send(message)  # Отправка сообщения в чат
        else:
            logger.error(f"Channel {channel} not found.")
            print(f"Channel {channel} not found.")

    @helpers.cooldown(7.5)
    async def echo_msg(self, channel, message):
        """Отправка эхо-сообщения."""
        channel_obj = self.get_channel(channel)
        if channel_obj:
            await channel_obj.send(message)  # Отправка сообщения в чат
        else:
            logger.error(f"Channel {channel} not found.")
            print(f"Channel {channel} not found.")

    async def load_emotes_task(self):
        """Загрузка эмодзи."""
        self.emotes = await helpers.load_emotes()

    async def schedule_load_emotes(self):
        """Запланированная задача для периодической загрузки эмодзи."""
        while True:
            await asyncio.sleep(3600)  # Подождать 3600 секунд перед повторной загрузкой эмодзи
            self.emotes = asyncio.create_task(self.load_emotes_task())

    async def save_word(self, channel_name, word):
        try:
            with self.application.app_context():
                channel = Channel.query.filter_by(name=channel_name).first()
                if not channel:
                    channel = Channel(name=channel_name)
                    db.session.add(channel)
                    db.session.commit()  # Фиксируем канал в БД перед созданием Emote

                # Теперь channel.id доступен
                emote = Emote.query.filter_by(name=word, channel_id=channel.id).first()
                if emote:
                    emote.count += 1
                else:
                    emote = Emote(name=word, count=1, channel=channel)  # Используем отношение
                    db.session.add(emote)
                
                db.session.commit()
        except Exception as e:
            logger.error(f'Error saving word: {str(e)}')
