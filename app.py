from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import time
import secrets
from math import ceil

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Create MySQL database connection
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="e-portfolio"
)

# Create contacts table if it does not exist
mycursor = mydb.cursor()
mycursor.execute("CREATE TABLE IF NOT EXISTS contacts (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), email VARCHAR(255), message TEXT, date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/projects")
def projects():
    return render_template("projects.html")

@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        # Insert form data into MySQL database
        mycursor = mydb.cursor()
        sql = "INSERT INTO contacts (name, email, message) VALUES (%s, %s, %s)"
        val = (name, email, message)
        mycursor.execute(sql, val)
        mydb.commit()

        return render_template("contact.html", success=True)

    return render_template("contact.html", success=False)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # проверяем введенные данные пользователя
        if request.form['username'] == 'admin' and request.form['password'] == 'password':
            session['logged_in'] = True
            session['username'] = request.form['username']
            return redirect(url_for('admin'))
        else:
            error = 'Неправильные имя пользователя или пароль'
            return render_template('login.html', error=error)
    return render_template('login.html')


@app.route('/logout')
def logout():
    session['logged_in'] = False
    return redirect(url_for('login'))


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    # проверяем, авторизован ли пользователь
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    # обработка параметров поиска
    name = request.args.get('name', '')
    date = request.args.get('date', '')
    mycursor = mydb.cursor()
    if name and date:
        sql = "SELECT * FROM contacts WHERE name=%s AND DATE(created_at)=%s ORDER BY created_at DESC"
        val = (name, date)
    elif name:
        sql = "SELECT * FROM contacts WHERE name=%s ORDER BY created_at DESC"
        val = (name,)
    elif date:
        sql = "SELECT * FROM contacts WHERE DATE(created_at)=%s ORDER BY created_at DESC"
        val = (date,)
    else:
        sql = "SELECT * FROM contacts ORDER BY created_at DESC"
        val = ()
    mycursor.execute(sql, val)
    contacts = mycursor.fetchall()
    return render_template('admin.html', contacts=contacts)

       
@app.route('/admin/delete/<int:id>', methods=['POST'])
def delete_message(id):
    # проверяем, авторизован ли пользователь
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    # удаляем сообщение из базы данных
    mycursor = mydb.cursor()
    sql = "DELETE FROM contacts WHERE id = %s"
    val = (id,)
    mycursor.execute(sql, val)
    mydb.commit()

    # возвращаем пользователя на страницу администратора
    return redirect(url_for('admin'))


@app.route('/admin/delete/confirm/<int:id>')
def confirm_delete(id):
    # проверяем, авторизован ли пользователь
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    # получаем информацию о сообщении из базы данных
    mycursor = mydb.cursor()
    sql = "SELECT * FROM contacts WHERE id = %s"
    val = (id,)
    mycursor.execute(sql, val)
    message = mycursor.fetchone()

    return render_template('confirm_delete.html', message=message)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

