from flask import Flask, request, jsonify

app = Flask(__name__)

# Хранение последних полученных данных
last_data = {}


# Эндпоинт для обработки вебхуков
@app.route('/webhook', methods=['POST'])
def webhook():
    global last_data
    last_data = request.json  # Сохраняем данные
    return 'Webhook received', 200


# Эндпоинт для получения последних данных
@app.route('/webhook', methods=['GET'])
def get_webhook_data():
    return jsonify(last_data)  # Возвращаем последние данные


if __name__ == '__main__':
    app.run(port=3000)
