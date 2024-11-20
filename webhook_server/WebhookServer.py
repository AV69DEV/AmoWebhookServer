from flask import Flask, request
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv
import logging
import sys
import os

logging.basicConfig(
    filename='/path/to/flask_server.log',
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
    x_for=1,      # Доверять 1 прокси для IP (X-Forwarded-For)
    x_proto=1,    # Доверять 1 прокси для протокола (X-Forwarded-Proto)
    x_host=1,     # Доверять 1 прокси для хоста (X-Forwarded-Host)
    x_prefix=1    # Доверять 1 прокси для префикса пути (X-Forwarded-Prefix)
)


@app.route('/webhooks/test', methods=['POST'])
def receive_webhook():
    headers = dict(request.headers)  # Получить все заголовки
    print("Заголовки запроса:", headers)
    if request.is_json:
        webhook_data = request.json
    else:
        webhook_data = request.form.to_dict()
    print("Получен вебхук:", webhook_data)
    return "Webhook received", 200


if __name__ == '__main__':
    app.run(port=3002)
