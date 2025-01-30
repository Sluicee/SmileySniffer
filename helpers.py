# helpers.py
# -*- coding: utf-8 -*-

import os
import requests
import asyncio
from functools import wraps
from dotenv import load_dotenv
import logging
from config import application, db
from models import Channel, Emote
import aiohttp

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    
logger = logging.getLogger('config')

API_URL_7TV = 'https://7tv.io/v3'
USERS_7TV_API = '/users/'
EMOTESETS_7TV_API = '/emote-sets/'
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

for item in items:
    parts = item.split("=")
    if len(parts) == 2:
        key = parts[0].strip().lower()
        value = parts[1].strip().lower()
        UID7TV[key] = value

async def get_7tv_user_emote_set_id(channel_id):
    url = API_URL_7TV + USERS_7TV_API + channel_id
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        logger.error(f'Error: {response.status_code}')
        return []

async def get_7tv_emotes(channel_id):
    emote_set = (await get_7tv_user_emote_set_id(channel_id))["emote_sets"][0]['id']
    async with aiohttp.ClientSession() as session:
        url = f"{API_URL_7TV}/emote-sets/{emote_set}"
        async with session.get(url) as response:
            return await response.json()

async def get_emotes(channel_id):
    emotes = await get_7tv_emotes(channel_id)
    return [
        {
            "name": emote["name"],
            "image_url": f'https://cdn.7tv.app/emote/{emote["id"]}/4x.webp'  # URL изображения
        }
        for emote in (emotes.get("emotes", []))
    ] if emotes else []

async def get_emote_names(emotes):
    return [emote['name'] for emote in emotes] if emotes else []

async def load_emotes():
    emotes_array = await asyncio.gather(*[load_emotes_for_channel(channel) for channel in UID7TV])
    
    logger.info("Emotes reloaded")
    print("Emotes reloaded")
    
    return emotes_array

def get_avatars():
    avatars = []
    for channel in CHANNELS:
        url = API_URL_7TV + USERS_7TV_API + UID7TV[channel]
        response = requests.get(url)
        if response.status_code == 200:
            avatars.append(response.json()['avatar_url'])
        else:
            avatars.append(None)  # Или значение по умолчанию
    return avatars

async def load_emotes_for_channel(channel):
    try:
        # Явно используем контекст приложения
        with application.app_context():
            channel_emotes = await get_emote_names(await get_emotes(UID7TV[channel]))
            
            # Очистка старых эмодзи
            channel_obj = Channel.query.filter_by(name=channel).first()
            if channel_obj:
                # Удаляем эмодзи, которых нет в текущем списке
                for emote in channel_obj.emotes:
                    if emote.name not in channel_emotes:
                        db.session.delete(emote)
                
                # Добавляем новые эмодзи
                existing_emotes = {e.name for e in channel_obj.emotes}
                for emote_name in channel_emotes:
                    if emote_name not in existing_emotes:
                        new_emote = Emote(name=emote_name, count=0, channel=channel_obj)
                        db.session.add(new_emote)
                
                db.session.commit()
            
            return channel_emotes
            
    except Exception as e:
        logger.error(f'Error loading emotes for channel {channel}: {e}')
        return []

def cooldown(seconds):
    def decorator(func):
        last_called = {}

        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            channel = args[0]  # предполагаем, что первый аргумент - канал
            now = asyncio.get_event_loop().time()
            if channel not in last_called or now - last_called[channel] >= seconds:
                last_called[channel] = now
                return await func(self, *args, **kwargs)
            else:
                logger.warning(f"Cooldown active for channel {channel}")
        return wrapper
    return decorator

def get_times_word(number):
    if 11 <= number % 100 <= 19:
        return 'раз'
    elif number % 10 == 1:
        return 'раз'
    elif 2 <= number % 10 <= 4:
        return 'раза'
    else:
        return 'раз'
