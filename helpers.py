# helpers.py
# -*- coding: utf-8 -*-

import os
import requests
import asyncio
from functools import wraps
from dotenv import load_dotenv
import logging
import json
import tempfile


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    
logger = logging.getLogger('flask_app')


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
DATA_DIR = os.getenv('DATA_DIR')

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

def load_emotes():
    emotes_array = []  # Создаем пустой двумерный массив для хранения смайликов по каналам
    for channel in UID7TV:
        emotes_for_channel = []  # Создаем пустой список для смайликов конкретного канала
        
        # Получаем смайлики для текущего канала
        channel_emotes = get_emote_names(get_emotes(UID7TV[channel]))
        
        # Добавляем смайлики в список emotes_for_channel
        emotes_for_channel.extend(channel_emotes)
        
        # Добавляем список смайликов текущего канала в двумерный массив
        emotes_array.append(emotes_for_channel)
        
        try:
            # Путь к файлу JSON для канала
            channel_filename = f'{channel}.json'
            channel_file_path = os.path.join(DATA_DIR, channel_filename)
            
            # Загрузка данных из файла JSON
            if os.path.exists(channel_file_path):
                with open(channel_file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
            else:
                data = {}
            
            # Оставляем только ключи, которые есть в emotes_for_channel
            keys_to_keep = set(emotes_for_channel)
            data = {key: value for key, value in data.items() if key in keys_to_keep}
            
            # Записываем обновленные данные во временный файл
            temp_file_path = None
            try:
                with tempfile.NamedTemporaryFile('w', delete=False, dir=DATA_DIR, suffix='.tmp', encoding='utf-8') as temp_file:
                    temp_file_path = temp_file.name
                    json.dump(data, temp_file, indent=4)
                
                # После успешной записи во временный файл, заменяем основной файл
                os.replace(temp_file_path, channel_file_path)
                print(f'Successfully updated {channel_filename}')
                
            except Exception as e:
                if temp_file_path and os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                raise e
        
        except Exception as e:
            print(f'Error updating {channel_filename}: {e}')
        
    logger.info("Emotes reloaded")
    print("Emotes reloaded")
    
    return emotes_array