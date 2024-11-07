from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import requests

load_dotenv()
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD').replace('@', '%40')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Модель для таблицы user_tokens
class UserToken(db.Model):
    __tablename__ = 'user_tokens'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(255), unique=True, nullable=False)
    access_token = db.Column(db.Text, nullable=False)
    refresh_token = db.Column(db.Text, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    referer = db.Column(db.Text)


# Создать таблицы, если они не существуют
with app.app_context():
    db.create_all()

# Хранение последних полученных данных
last_data = {}


# Callback для обработки кода авторизации и сохранения токенов
@app.route('/oauth/callback')
def oauth_callback():
    app.logger.info(request.args)
    code = request.args.get('code')
    referer = request.args.get('referer')
    print(f'code: {code}\nreferer: {referer}')

    if not code or not referer:
        return "Ошибка: код или referrer не передан", 400

    # Получение access_token
    token_url = f"https://{os.getenv('AMOCRM_DOMAIN')}.amocrm.ru/oauth2/access_token"
    data = {
        "client_id": os.getenv('CLIENT_ID'),
        "client_secret": os.getenv('CLIENT_SECRET'),
        "code": code,
        "redirect_uri": os.getenv('REDIRECT_URI'),
        "grant_type": "authorization_code"
    }

    response = requests.post(token_url, data=data)
    if response.status_code == 200:
        tokens = response.json()
        access_token = tokens.get('access_token')
        refresh_token = tokens.get('refresh_token')
        expires_in = tokens.get('expires_in', 0)  # Установка 0, если отсутствует
        if not access_token or not refresh_token:
            return "Ошибка: не удалось получить токены", 400

        expires_at = datetime.now() + timedelta(seconds=expires_in)

        # Сохранение токенов в базе данных с использованием SQLAlchemy
        user_token = UserToken.query.filter_by(referer=referer).first()
        if user_token:
            # Обновление токенов для существующего пользователя
            user_token.access_token = access_token
            user_token.refresh_token = refresh_token
            user_token.expires_at = expires_at
        else:
            # Создание новой записи для нового пользователя
            user_token = UserToken(
                referer=referer,
                access_token=access_token,
                refresh_token=refresh_token,
                expires_at=expires_at
            )
            db.session.add(user_token)

        db.session.commit()

        return "Авторизация успешна и токены сохранены в базе данных!"
    else:
        return f"Ошибка при получении токенов: {response.status_code} - {response.text}"


# Эндпоинт для обработки вебхуков
@app.route('/webhook', methods=['POST'])
def webhook():
    global last_data
    if request.content_type == 'application/x-www-form-urlencoded':
        # Получаем данные из формы и сохраняем их
        last_data = request.form.to_dict()
        return 'Webhook received', 200
    else:
        return 'Unsupported Media Type', 415


# Эндпоинт для получения последних данных
@app.route('/webhook', methods=['GET'])
def get_webhook_data():
    return jsonify(last_data)  # Возвращаем последние данные


if __name__ == '__main__':
    app.run(port=3000)
