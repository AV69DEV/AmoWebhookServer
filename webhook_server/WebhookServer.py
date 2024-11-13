from flask import Flask, request
from dotenv import load_dotenv
import os

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
app = Flask(__name__, static_folder=os.getenv('STATIC_FOLDER'),
            template_folder=os.getenv('TEMPLATE_FOLDER'))


@app.route('/webhooks/test', methods=['POST'])
def receive_webhook():
    if request.is_json:
        webhook_data = request.json
    else:
        webhook_data = request.form.to_dict()
    print("Получен вебхук:", webhook_data)
    return "Webhook received", 200


if __name__ == '__main__':
    app.run(port=3002)
