from flask import Flask, render_template
import json

app = Flask(__name__)

@app.route('/')
def index():
    # Загрузка данных из файла
    with open('path_to_data.json', 'r') as file:
        data = json.load(file)

    # Получение списка пользователей
    users = data['joinedUsers']

    # Отображение списка пользователей на веб-странице
    return render_template('index.html', users=users)

if __name__ == '__main__':
    app.run(debug=True)
