import json
import os

from flask import Flask, render_template

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'data.json')

app = Flask(__name__, template_folder=BASE_DIR)


def load_users():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as file:
            return json.load(file).get('joinedUsers', {})
    except FileNotFoundError:
        return {}


@app.route('/')
def index():
    return render_template('index.html', users=load_users())


if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG') == '1')
