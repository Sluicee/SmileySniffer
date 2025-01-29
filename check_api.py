import requests
import os

# Загружаем переменные окружения
from dotenv import load_dotenv
load_dotenv()

# Список каналов
CHANNELS = os.getenv("CHANNELS").split(",")
UID7TV = {item.split("=")[0].strip().lower(): item.split("=")[1].strip() for item in os.getenv("UID7TV").split(",")}

# Проверка доступности API для каждого канала
def check_api():
    for channel in CHANNELS:
        channel_id = UID7TV.get(channel.strip().lower())
        if channel_id:
            # Проверка получения информации о пользователе
            user_url = f"https://7tv.io/v3/users/{channel_id}"
            response = requests.get(user_url)
            if response.status_code == 200:
                print(f"{channel} - доступен")
            else:
                print(f"{channel} - ошибка: {response.status_code}")
        else:
            print(f"{channel} - не найден в UID7TV")

check_api()
