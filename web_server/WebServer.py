from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from werkzeug.middleware.proxy_fix import ProxyFix
import logging
import sys
from dotenv import load_dotenv
import os

logging.basicConfig(
    filename='/var/www/dev/AmoWebhookServer/logs/web_server/main.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)


# Перенаправление stdout и stderr в лог
class LogRedirector:
    def write(self, message):
        if message.strip():  # Игнорировать пустые строки
            logging.info(message)

    def flush(self):  # Необходим метод для совместимости
        pass


sys.stdout = LogRedirector()
sys.stderr = LogRedirector()

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
app = Flask(__name__, static_folder=os.getenv('STATIC_FOLDER'),
            template_folder=os.getenv('TEMPLATE_FOLDER'))

app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=1,  # Доверять 1 прокси для IP (X-Forwarded-For)
    x_proto=1,  # Доверять 1 прокси для протокола (X-Forwarded-Proto)
    x_host=1,  # Доверять 1 прокси для хоста (X-Forwarded-Host)
    x_prefix=1  # Доверять 1 прокси для префикса пути (X-Forwarded-Prefix)
)


@app.route('/site/home', methods=['GET'])
def site():
    headers = dict(request.headers)  # Получить все заголовки
    print("Заголовки запроса:", headers)
    client_id = os.getenv('CLIENT_ID')
    redirect_uri = os.getenv('REDIRECT_URI')
    return render_template('site.html', client_id=client_id, redirect_uri=redirect_uri)


if __name__ == '__main__':
    app.run(port=3001)
