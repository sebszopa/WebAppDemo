from flask import Flask, render_template, request, jsonify, redirect, url_for, abort
from bcrypt import hashpw, gensalt
import sqlite3
import os
# importing repleacing string library
import re

# Databases connection config file
from config import SQLITE_DB

app = Flask(__name__)

# Home Page
@app.route('/')
def index():
    return render_template('index.html')

# Displaying system users from SQLite database
@app.route('/system')
def get_sysusers():
    with sqlite3.connect(SQLITE_DB) as conn:
        conn.row_factory = sqlite3.Row  # changing from data index to name
        cursor = conn.cursor()
        cursor.execute('SELECT "su_id", "email", "name", "surname", "role" FROM "sys_usrs";')
        rows = cursor.fetchall()
        for row in rows:
            print(dict(row))  #
    return render_template('sysusers.html', rows=rows)

# Form to add system users
@app.route('/system/users/add', methods=['GET'])
def sysuser_add_form():
    return render_template('sysuser_add_form.html')

# Adding user to SQLite database
@app.route('/system/users/added', methods=['POST'])
def add_sysuser():
    # Collecting data from the form
    name = request.form.get('name', '').strip()
    surname = request.form.get('surname', '').strip()
    email = request.form.get('email', '').strip()
    role = request.form.get('role', 'user').strip()  # Default role
    password = request.form.get('password', '').strip()

    # Data validation - checking for empty fields
    if not all([name, surname, email, password]):
        return jsonify({"error": "All fields must be filled."}), 400

    # Email form validation
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({"error": "Invalid email format."}), 400

    # Password length validation
    if len(password) < 8:
        return jsonify({"error": "The password must be at least 8 characters long."}), 400

    # Password encryption
    hashed_password = hashpw(password.encode('utf-8'), gensalt())

    try:
        # Establishing connection with SQLite
        with sqlite3.connect(SQLITE_DB) as conn:
            cursor = conn.cursor()
            sql = """
            INSERT INTO sys_usrs (email, name, surname, role, passwd)
            VALUES (?, ?, ?, ?, ?)
            """
            values = (email, name, surname, role, hashed_password)
            cursor.execute(sql, values)
            conn.commit()

            print(f"User {name} {surname} has been added.")

    except sqlite3.IntegrityError as e:
        print(f"Duplicate email: {e}")
        return jsonify({"error": "The email already exists."}), 400

    except sqlite3.Error as e:
        logging.exception("Database error occurred")
        return jsonify({"error": "There was an error whie adding the data."}), 500

    return render_template('sysuser_added.html', name=name, surname=surname, email=email, role=role)

@app.route('/system/users/more', methods=['GET', 'POST'])
def user_more_details():
    su_id = request.form.get('su_id')  # Zmieniamy na request.form.get() dla danych przesyłanych metodą POST

    if su_id is None:
        return "No user id provided", 400  # Dodajemy walidację, aby upewnić się, że su_id zostało przesłane

    with sqlite3.connect(SQLITE_DB) as conn:
        conn.row_factory = sqlite3.Row  # Zmieniamy na słownik dla łatwiejszego dostępu
        cursor = conn.cursor()
        cursor.execute('SELECT "su_id", "email", "name", "surname", "role" FROM "sys_usrs" WHERE su_id = ?', (su_id,))
        row = cursor.fetchone()  # Pobieramy tylko jeden wiersz
        if row:
            return render_template('sysuser_mod_form.html', row=row)  # Upewnij się, że przekazujesz 'row'
        else:
            return "User not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=True, use_reloader=False)
