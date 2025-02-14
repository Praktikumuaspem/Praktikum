from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Konfigurasi MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''  # Ganti dengan password MySQL Anda
app.config['MYSQL_DB'] = 'flask_crud'

mysql = MySQL(app)

# Halaman login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cur.fetchone()
        cur.close()
        
        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            flash('Login berhasil!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Username atau password salah', 'danger')
    return render_template('login.html')

# Halaman logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logout berhasil!', 'info')
    return redirect(url_for('login'))

# Halaman utama
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM items")
    items = cur.fetchall()
    cur.close()
    return render_template('index.html', items=items)

# Menambah item
@app.route('/add', methods=['POST'])
def add_item():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    name = request.form['name']
    stock = request.form['stock']
    price = request.form['price']
    
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO items (name, stock, price) VALUES (%s, %s, %s)", (name, stock, price))
    mysql.connection.commit()
    cur.close()
    
    flash('Item berhasil ditambahkan!', 'success')
    return redirect(url_for('index'))

# Menghapus item
@app.route('/delete/<int:id>')
def delete_item(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM items WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    flash('Item berhasil dihapus!', 'warning')
    return redirect(url_for('index'))

# Registrasi user
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        mysql.connection.commit()
        cur.close()
        flash('Registrasi berhasil! Silakan login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)
