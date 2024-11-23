# !!! Test system user test1@test2.com pass test1234

from flask import Flask, render_template, request, jsonify, redirect, url_for, abort, session, flash, get_flashed_messages
from bcrypt import hashpw, gensalt, checkpw
from functools import wraps
import sqlite3
import os
# importing repleacing string library
import re

# Databases connection config file
from config import SQLITE_DB

app = Flask(__name__)
app.secret_key = 'uwjs9wksk'

### LOGGIN SECTION AND SESSIONS ###
# login in form processing
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# login out - end of session
@app.route('/logout')
def logout():
    # Usuń dane użytkownika z sesji
    session.pop('username', None)
    return redirect(url_for('index'))

# checking system user in SQLite databese

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect(SQLITE_DB) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT email, passwd FROM sys_usrs WHERE email=?", (username,))
            result = cursor.fetchone()

            if result and checkpw(password.encode('utf-8'), result[1]):
                # Autentication - verfied user
                session['username'] = username
                return redirect(url_for('index'))
            else:
                # Unathenticatd user
                return render_template('index.html', title='Login Failed')

    elif request.method == 'GET':
        if 'username' in session:
            # If user logged in
            return redirect(url_for('index'))
        else:
            # Show login form
            return render_template('index.html', title='Login')

    else:
        abort(405)
# Ner section - logged in user area onlu
@app.route('/dashboard')
@login_required
def dashboard():

    # Eventually tp change for designeted html logged user page
    return render_template('index.html', username=session['username'])

### END OF LOGN SECTION ###

# Home Page
# UPDATED - Displaing messeges if they exists
# Used flash metchod for messeges
@app.route('/')
def index():
    messages = get_flashed_messages(with_categories=True)
    return render_template('index.html', messages=messages)

# Displaying system users from SQLite database
# Changned the method how users data are diplayed
# New table column - nameed - "More" sendig the hidden form to user details page

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

# New feture - updating users Details
@app.route('/system/users/more', methods=['GET', 'POST'])
def user_more_details():
    su_id = request.form.get('su_id')

# checking if su_id has been post
    if su_id is None:
        flash("No user id provided", 400)
        return redirect(url_for('index'))

# collecting one user details form SQLite
# Next feautre - collecting related user data from MongoDB to displau at the same page

    with sqlite3.connect(SQLITE_DB) as conn:
        conn.row_factory = sqlite3.Row  # Change to names
        cursor = conn.cursor()
        cursor.execute('SELECT "su_id", "email", "name", "surname", "role" FROM "sys_usrs" WHERE su_id = ?', (su_id,))
        row = cursor.fetchone()  # Picking up just one row
        if row:
            return render_template('sysuser_mod_form.html', row=row)  # rendering row details
        else:
            flash("User not found", 404)
            return redirect(url_for('index'))

### UPDATING USERR PASSWORD IN SQLite ###
@app.route('/system/users/update_pwd', methods=['POST'])
def update_password():
    # Collecting password from form
    pwd1 = request.form.get('pwd1')
    pwd2 = request.form.get('pwd2')
    su_id = request.form.get('su_id')

    # Checking password missmatch
    if pwd1 != pwd2:
        flash("Passwords do not match. Please try again.", "error")
        return redirect(url_for('index'))

    # Encoding password
    hashed_pwd = hashpw(pwd1.encode('utf-8'), gensalt())

    # Updating pwd field in SQLite databes with matching su_id
    with sqlite3.connect(SQLITE_DB) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE sys_usrs SET passwd = ? WHERE su_id = ?", (hashed_pwd, su_id))
            conn.commit()
            flash("Password updated successfully.", "success")
        except sqlite3.Error as e:
            flash(f"An error occurred: {e}", "error")
            return redirect(url_for('index'))

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=True, use_reloader=False)
