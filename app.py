from flask import Flask, render_template, request, redirect, url_for, session
import random
import string

app = Flask(__name__)
app.secret_key='supersecretkey'

USERS = [
    {'login': "admin", "password": "admin"},
    {'login': 'user', 'password': 'qwerty'}    
]

def checkl(login,password):
    for user in USERS:
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

    password = ''.join(random.choice(chars) for _ in range(length))
    return password

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        if checkl(login, password):
            session['user'] = login
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Неверный логин или пароль')
    return render_template('login.html')

@app.route('/generator', methods=['GET', 'POST'])
def index():
    if 'user' not in session:
        return redirect(url_for('login'))

    passwords = []
    if request.method == 'POST':
        try:
            length = int(request.form['length'])
            count = int(request.form['count'])
            complexity = request.form['complexity']
            with open("password_history.txt", "a", encoding="utf-8") as f:
                for _ in range(count):
                    pwd = generate_password(length, complexity)
                    passwords.append(pwd)
                    f.write(f"{session['user']} | {pwd}\n")
        except:
            passwords = ["Ошибка ввода. Попробуйте ещё раз."]

    return render_template('index.html', passwords=passwords, user=session['user'])

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=7000)
