import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Загрузка переменных окружения
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    from dotenv import load_dotenv
    load_dotenv(dotenv_path)

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['ASSETS_DEBUG'] = True
    app.debug = True

    db.init_app(app)

    with app.app_context():
        db.create_all()  # Создаёт новые таблицы
        print("Таблицы созданы!")  # Подтверждение

    return app

application = create_app()