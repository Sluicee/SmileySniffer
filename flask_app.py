import os
import helpers
from flask import Flask, request, jsonify, render_template, send_file
from dotenv import load_dotenv
from flask_assets import Environment, Bundle
from bot import bot
import json

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    
UID7TV = dict(item.split("=") for item in os.getenv("UID7TV").split(","))
CHANNELS = os.getenv('CHANNELS').split(',')
DATA_DIR = os.getenv('DATA_DIR')
# Установка пути к каталогу для хранения JSON файлов смайликов


app = Flask(__name__)
app.config['ASSETS_DEBUG'] = True

assets = Environment(app)

assets.register('main_css', Bundle('styles/main.css', output='gen/main.css'))
assets.register('main_js', Bundle('scripts/main.js', output='gen/main.js'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/channels', methods=['GET'])
def get_channels():
    return CHANNELS

@app.route('/<channel_name>')
def get_channel(channel_name):
    if channel_name in CHANNELS:
        return render_template('channel.html', channel_name=channel_name)
    else:
        return "Чат не найден", 404

@app.route('/<channel_name>/messages', methods=['GET'])
def get_messages_by_channel(channel_name):
    if channel_name in CHANNELS:
        last_request_time = float(request.args.get('last_request_time', 0))
        new_messages = [msg for msg in bot.messages if msg['channel'] == channel_name and msg['timestamp'] > last_request_time]
        return jsonify(new_messages)
    else:
        return "Чат не найден", 404


@app.route('/<channel_name>/emotes', methods=['GET'])
def get_emotes_by_channel(channel_name):
    if channel_name in CHANNELS:
        data = jsonify(list(helpers.get_emotes(UID7TV[channel_name])))
        return data
    else:
        return "Emotes не найдены", 404

@app.route('/download/<channel>.json', methods=['GET'])
def download_json(channel):
    channel_file_path = os.path.join(DATA_DIR, f'{channel}.json')
    
    if os.path.exists(channel_file_path):
        try:
            with open(channel_file_path, 'r') as file:
                data = json.load(file)
            return jsonify(data)
        except Exception as e:
            return jsonify({'status': 'Failed to send file', 'error': str(e)}), 500
    else:
        return jsonify({'status': 'File not found'}), 404

@app.route('/send', methods=['POST'])
def send_message():
    data = request.json
    channel = data.get('channel')
    message = data.get('message')
    if channel and message:
        bot.loop.create_task(bot.send_message(channel, message))
        return jsonify({'status': 'Message sent'})
    return jsonify({'status': 'Failed to send message'}), 400

# @app.route('/save_word', methods=['POST'])
# def save_word():
#     data = request.json
#     print('Received data:', data)
#     if 'word' not in data or 'channel' not in data:
#         print('Invalid data received')
#         return jsonify({'status': 'Invalid data received'}), 400

#     word = data['word']
#     channel = data['channel']
    
#     # Создание имени JSON файла для данного канала
#     channel_filename = f'{channel}.json'
#     channel_file_path = os.path.join(DATA_DIR, channel_filename)
    
#     try:
#         # Создание или обновление JSON файла
#         if os.path.exists(channel_file_path):
#             with open(channel_file_path, 'r+') as file:
#                 data = json.load(file)
#                 data[word] = data.get(word, 0) + 1
#                 file.seek(0)
#                 json.dump(data, file, indent=4)
#         else:
#             with open(channel_file_path, 'w') as file:
#                 json.dump({word: 1}, file, indent=4)
        
#         print('Word saved successfully')
#         return jsonify({'status': 'Word saved successfully'}), 200
#     except Exception as e:
#         print('Error saving word:', str(e))
#         return jsonify({'status': 'Error saving word', 'error': str(e)}), 500

