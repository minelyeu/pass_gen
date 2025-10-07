from flask import Flask, render_template, request
import random
import string

app = Flask(__name__)

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
def index():
    passwords = []

    if request.method == 'POST':
        try:
            length = int(request.form['length'])
            count = int(request.form['count'])
            complexity = request.form['complexity']

            for _ in range(count):
                pwd = generate_password(length, complexity)
                passwords.append(pwd)

        except:
            passwords = ["Ошибка ввода. Попробуйте ещё раз."]

    return render_template('index.html', passwords=passwords)

if __name__ == '__main__':
    app.run(debug=True)
