# helpers.py

import os
import requests
import asyncio
from functools import wraps

API_URL_7TV = 'https://7tv.io/v3'
USERS_7TV_API = '/users/'
EMOTESETS_7TV_API = '/emote-sets/'
UID7TV = dict(item.split("=") for item in os.getenv("UID7TV").split(","))

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

def get_emote_names(emo):
    emotes = []
    for i in range(len(emo)):
        emotes.append(emo[i]['name'])
    if emotes:
        return emotes
    else:
        print('No emotes found')
    


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
                print(f"Cooldown active for channel {channel}")
        return wrapper
    return decorator
