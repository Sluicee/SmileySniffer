from models import Channel, Emote  # Импорт из models.py
from config import application, db
import json
import os

DATA_DIR = os.getenv('DATA_DIR')

with application.app_context():
    for filename in os.listdir(DATA_DIR):
        if filename.endswith('.json'):
            channel_name = filename.split('.')[0]
            with open(os.path.join(DATA_DIR, filename)) as f:
                data = json.load(f)

            # Проверка, существует ли канал
            channel = Channel.query.filter_by(name=channel_name).first()
            
            if not channel:
                # Если канал не существует, создаём новый
                channel = Channel(name=channel_name)
                db.session.add(channel)
                db.session.commit()  # Коммитим новый канал
            
            # Теперь добавляем или обновляем эмодзи для канала
            for name, count in data.items():
                emote = Emote.query.filter_by(name=name, channel_id=channel.id).first()
                if emote:
                    # Если эмодзи существует, обновляем его количество
                    emote.count = count
                else:
                    # Если эмодзи нет, создаём новый
                    emote = Emote(name=name, count=count, channel=channel)
                    db.session.add(emote)
            
            db.session.commit()  # Коммитим изменения по эмодзи
