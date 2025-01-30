import logging
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text

# Загрузка переменных окружения
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    from dotenv import load_dotenv
    load_dotenv(dotenv_path)

db = SQLAlchemy()

def configure_logging():
    if not os.path.exists('logs'):
        os.makedirs('logs')
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("logs/app.log"),
            logging.StreamHandler()
        ]
    )

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['ASSETS_DEBUG'] = True
    app.debug = True

    engine = create_engine(os.getenv('DATABASE_URL'))
    # Открываем соединение и выполняем запрос
    with engine.connect() as connection:
        result = connection.execute(text("SELECT current_user;"))
        user = result.scalar()  # Получаем одного пользователя
        print(f"Текущий пользователь: {user}")

    db.init_app(app)

    configure_logging()

    with app.app_context():
        db.create_all()  # Создаёт новые таблицы
        print("Таблицы созданы!")  # Подтверждение

    return app

application = create_app()

