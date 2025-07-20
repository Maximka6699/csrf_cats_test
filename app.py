from flask import Flask, request, session, redirect, url_for, render_template_string, abort, flash
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.static_folder = 'static'

# Простейшая "база данных"
users = {
    'admin': {'password': 'adminpass', 'balance': 10000},
    'user': {'password': 'userpass', 'balance': 0}
}

# HTML-шаблоны
login_template = """
<!doctype html>
<title>Login</title>
<h1>Login</h1>
<form method="post">
  Username: <input name="username"><br>
  Password: <input type="password" name="password"><br>
  <input type="submit" value="Login">
</form>
"""

bank_template = """
<!doctype html>
<title>Bank</title>
<h1>Welcome {{ username }}</h1>
<p>Balance: {{ balance }}</p>

<h2>Send Money</h2>
<form method="get" action="{{ url_for('transfer') }}">
  To: <input name="to"><br>
  Amount: <input name="amount"><br>
  <input type="submit" value="Transfer">
</form>

<p><a href="{{ url_for('shop') }}">Go to shop</a></p>
<p><a href="{{ url_for('logout') }}">Logout</a></p>
"""

shop_template = """
<!doctype html>
<title>Shop</title>
<h1>Secret Shop</h1>
<form method="post">
  <button type="submit">Buy flag for 10000</button>
</form>
<p><a href="{{ url_for('bank') }}">Back to bank</a></p>
<p>admin like CATS</p>
"""

cats_template = """
<!doctype html>
<title>Cats</title>
<h1>Cats</h1>
{% for cat in cats %}
  <div>
    <img src="{{ url_for('static', filename=cat['img']) }}" width="100"><br
    <p>{{ cat['name']|safe }}</p>
  </div>
{% endfor %}
"""

set_template = """
<!doctype html>
<title>Set Cat Name</title>
<h1>Изменить имя кота</h1>
<form method="post">
  ID: <input name="id"><br>
  Новое имя: <input name="name"><br>
  <button type="submit">Сохранить</button>
</form>
<p><a href="{{ url_for('view_cats') }}">Назад к котам</a></p>
"""

# Котики
cats = [
    {'img': 'cat1.jpg', 'name': 'Мурзик'},
    {'img': 'cat2.jpg', 'name': 'SETmyNme'},
]

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']
        if u in users and users[u]['password'] == p:
            session['user'] = u
            return redirect(url_for('bank'))
        else:
            return "Invalid credentials", 403
    return render_template_string(login_template)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/bank')
def bank():
    if 'user' not in session:
        return redirect(url_for('login'))
    username = session['user']
    return render_template_string(bank_template, username=username, balance=users[username]['balance'])

@app.route('/transfer', methods=['GET'])
def transfer():
    if 'user' not in session:
        return redirect(url_for('login'))
    sender = session['user']
    to = request.args.get('to')
    amount_str = request.args.get('amount', '0')

    try:
        amount = int(amount_str)
    except ValueError:
        return redirect(url_for('bank', error="Amount must be a number."))

    if not to or to not in users:
        return redirect(url_for('bank', error="Invalid recipient."))
    if amount <= 0 or users[sender]['balance'] < amount:
        return redirect(url_for('bank', error="Invalid amount or insufficient funds."))

    users[sender]['balance'] -= amount
    users[to]['balance'] += amount

    return redirect(url_for('bank'))

@app.route('/shop', methods=['GET', 'POST'])
def shop():
    if 'user' not in session:
        return redirect(url_for('login'))
    username = session['user']
    message = ""
    if request.method == 'POST':
        if users[username]['balance'] >= 10000:
            users[username]['balance'] -= 10000
            return '<script>alert("FLAG-CTF{you_got_the_flag}");</script>'
        else:
            message = "Not enough money"
    return render_template_string(shop_template, message=message)

@app.route('/cats', methods=['GET', 'POST'])
def view_cats():
    if 'user' not in session:
        return redirect(url_for('login'))

    # if request.method == 'POST':
    #     idx = int(request.form['id'])
    #     new_name = request.form['name']
    #     if 0 <= idx < len(cats):
    #         cats[idx]['name'] = new_name

    return render_template_string(cats_template, cats=cats)

@app.route('/cats/set', methods=['GET', 'POST'])
def set_cat():
    if request.method == 'POST':
        idx = int(request.form['id'])
        name = request.form['name']
        if 0 <= idx < len(cats):
            cats[idx]['name'] = name
        return redirect(url_for('view_cats'))
    return render_template_string(set_template)

if __name__ == '__main__':
    app.run(host = "0.0.0.0", port=5050 , debug=True)
