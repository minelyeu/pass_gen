from flask import Flask, render_template, request, redirect, url_for, session
import random
import string
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

USERS_FILE = "users.txt"
HISTORY_DIR = "user_history"

if not os.path.exists(HISTORY_DIR):
    os.makedirs(HISTORY_DIR)

def load_users():
    users = []
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split("|")
                if len(parts) >= 2:
                    login, password = parts[0], parts[1]
                    users.append({'login': login, 'password': password})
    return users


def save_user(login, password):
    with open(USERS_FILE, "a", encoding="utf-8") as f:
        f.write(f"{login}|{password}\n")


def user_exists(login):
    users = load_users()
    return any(u['login'] == login for u in users)


def check_user(login, password):
    users = load_users()
    for user in users:
        if user['login'] == login and user['password'] == password:
            return True
    return False

def generate_password(length, complexity):
    if complexity == "low":
        chars = string.ascii_lowercase
    elif complexity == "medium":
        chars = string.ascii_letters
    elif complexity == "high":
        chars = string.ascii_letters + string.digits
    else:  # max
        chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(chars) for _ in range(length))

@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']

        if user_exists(login):
            return render_template('register.html', error='Пользователь уже существует')

        save_user(login, password)
        session['user'] = login
        return redirect(url_for('index'))

    return render_template('register.html')


@app.route('/generator', methods=['GET', 'POST'])
def index():
    if 'user' not in session:
        return redirect(url_for('register'))

    user = session['user']
    passwords = []

    if request.method == 'POST':
        # Если нажата кнопка "Сгенерировать"
        if 'generate' in request.form:
            try:
                length = int(request.form['length'])
                count = int(request.form['count'])
                complexity = request.form['complexity']

                # просто генерируем пароли — без site/login
                for _ in range(count):
                    pwd = generate_password(length, complexity)
                    passwords.append(pwd)

            except Exception as e:
                passwords = [f"Ошибка: {e}"]

        # Если нажата кнопка "Сохранить"
        elif 'save' in request.form:
            site = request.form.get('site', '')
            login_name = request.form.get('login', '')
            selected = request.form.getlist('selected_passwords')

            history_path = os.path.join(HISTORY_DIR, f"history_{user}.txt")
            with open(history_path, "a", encoding="utf-8") as f:
                for pwd in selected:
                    f.write(f"site: {site} | login: {login_name} | password: {pwd}\n")

            return render_template('index.html', passwords=[], user=user, message="Сохранено!")

    return render_template('index.html', passwords=passwords, user=user)


@app.route('/history')
def history():
    if 'user' not in session:
        return redirect(url_for('register'))

    user = session['user']
    history_path = os.path.join(HISTORY_DIR, f"history_{user}.txt")

    if os.path.exists(history_path):
        with open(history_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    else:
        lines = ["История пуста."]

    return render_template('history.html', history=lines, user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']

        if check_user(login, password):
            session['user'] = login
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Неверный логин или пароль')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('register'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=7000)