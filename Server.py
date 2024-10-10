from flask import Flask, request, jsonify

app = Flask(__name__)

# Хранение последних полученных данных
last_data = {}


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
