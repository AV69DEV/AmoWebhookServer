from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import requests

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
app = Flask(__name__)

app.config[
    'SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD').replace('@', '%40')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
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


# Callback для обработки кода авторизации и сохранения токенов
@app.route('/oauth/callback')
def oauth_callback():
    app.logger.info(request.args)
    code = request.args.get('code')
    referer = request.args.get('referer')

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


@app.route('/oauth/update_token', methods=['POST'])
def update_token():
    app.logger.info("Получены параметры:", request.json)
    id = request.json.get('id')
    refresh_token = request.json.get('refresh_token')
    print(f"параметры запроса:{request.json}")
    if not id or not refresh_token:
        return "Ошибка: ID пользователя или refresh_token не переданы", 400

    refresh_token_url = f"https://{os.getenv('AMOCRM_DOMAIN')}.amocrm.ru/oauth2/access_token"
    data = {
        "client_id": os.getenv('CLIENT_ID'),
        "client_secret": os.getenv('CLIENT_SECRET'),
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "redirect_uri": os.getenv('REDIRECT_URI')
    }
    print(f"Данные для отправки на сервер авторизации амо:\n{data}")
    response = requests.post(refresh_token_url, data=data)
    if response.status_code == 200:
        tokens = response.json()
        access_token = tokens.get('access_token')
        refresh_token = tokens.get('refresh_token')
        expires_in = tokens.get('expires_in', 0)

        if not access_token or not refresh_token:
            app.logger.error("Токены не получены из ответа: %s", tokens)
            return "Ошибка: не удалось получить токены", 400

        expires_at = datetime.now() + timedelta(seconds=expires_in)
        user_token = UserToken.query.filter_by(id=id).first()

        if user_token is None:
            app.logger.warning("Пользователь с ID %s не найден", id)
            return "Ошибка: пользователь не найден", 404

        user_token.access_token = access_token
        user_token.refresh_token = refresh_token
        user_token.expires_at = expires_at

        db.session.commit()
        return jsonify({"access_token": access_token}), 200

    else:
        app.logger.error("Ошибка при обновлении токенов: %s", response.text)
        return "Ошибка: не удалось обновить токен", response.status_code


if __name__ == '__main__':
    app.run(port=3000)
