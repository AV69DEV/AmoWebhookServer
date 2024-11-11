from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from dotenv import load_dotenv
import os

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
app = Flask(__name__, static_folder='/var/www/dev/AmoWebhookServer/static',
            template_folder='/var/www/dev/AmoWebhookServer/templates')


@app.route('/site/home', methods=['GET'])
def site():
    client_id = os.getenv('CLIENT_ID')
    redirect_uri = os.getenv('REDIRECT_URI')
    return render_template('site.html', client_id=client_id, redirect_uri=redirect_uri)


if __name__ == '__main__':
    app.run(port=3001)
