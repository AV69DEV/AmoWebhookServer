from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)


@app.route('/site', methods=['GET'])
def site():
    client_id = os.getenv('CLIENT_ID')
    redirect_uri = os.getenv('REDIRECT_URI')
    return render_template('site.html', client_id=client_id, redirect_uri=redirect_uri)


if __name__ == '__main__':
    app.run(port=3001)
