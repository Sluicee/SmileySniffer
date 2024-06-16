# helpers.py
# -*- coding: utf-8 -*-

import os
import requests
import asyncio
from functools import wraps
from dotenv import load_dotenv
import logging


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    
logger = logging.getLogger('flask_app')


API_URL_7TV = 'https://7tv.io/v3'
USERS_7TV_API = '/users/'
EMOTESETS_7TV_API = '/emote-sets/'
env_value = os.getenv("UID7TV")
items = env_value.split(",") if env_value else []
UID7TV = {}
for item in items:
    parts = item.split("=")
    if len(parts) == 2:
        key = parts[0].strip().lower()
        value = parts[1].strip().lower()
        UID7TV[key] = value

# Функция для получения id набора смайликов пользователя из 7TV API
def get_7tv_user_emote_set_id(channel_id):
    url = API_URL_7TV + USERS_7TV_API + channel_id
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        logger.error(f'Error: {response.status_code}')
        return []

# Функция для получения списка смайликов из 7TV API
def get_7tv_emotes(channel_id):
    emote_set = get_7tv_user_emote_set_id(channel_id)["emote_sets"][0]['id']
    url = API_URL_7TV + EMOTESETS_7TV_API + emote_set
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        logger.error(f'Error: {response.status_code}')
        return []

# Функция для получения смайликов из 7TV API
def get_emotes(channel_id):
    emotes = get_7tv_emotes(channel_id)['emotes']
    if emotes:
        return emotes
    else:
        logger.error('No emotes found')

def get_emote_names(emo):
    emotes = []
    for i in range(len(emo)):
        emotes.append(emo[i]['name'])
    if emotes:
        return emotes
    else:
        logger.error('No emotes found')
    


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
