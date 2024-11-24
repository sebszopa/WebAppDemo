from flask import Flask, render_template, request, jsonify, redirect, url_for, abort, session, flash, get_flashed_messages
from bcrypt import hashpw, gensalt, checkpw
from functools import wraps
from pymongo import MongoClient
import pandas as pd
import os
import sqlite3
import re

# Databases connection config file
from config import MONGO_URI, SQLITE_DB

# Establishing connection with MongoDB
client = MongoClient(os.getenv("MONGO_URI"))

# Selecting Database
db = client["ssdev001"]

# Picking up the collection
mongo_collection = db["patient01"]

app = Flask(__name__)
app.secret_key = 'uwjs9wksk'

### LOGGIN SECTION AND SESSIONS ###
# Login form
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
# logging out
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))
# checkig user and password in SQLIte database
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
                session['username'] = username
                return redirect(url_for('index'))
            else:
                return render_template('index.html', title='Login Failed')

    elif request.method == 'GET':
        if 'username' in session:
            return redirect(url_for('index'))
        else:
            return render_template('index.html', title='Login')
    else:
        abort(405)
# route to logged user dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('index.html', username=session['username'])

@app.route('/')
def index():
    messages = get_flashed_messages(with_categories=True)
    return render_template('index.html', messages=messages)

@app.route('/system')
def get_sysusers():
    with sqlite3.connect(SQLITE_DB) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT "su_id", "p_id", "email", "name", "surname", "role" FROM "sys_usrs";')
        rows = cursor.fetchall()
        for row in rows:
            print(dict(row))  # Debug: Wyświetlanie wyników zapytania w terminalu
    return render_template('sysusers.html', rows=rows)

@app.route('/system/users/add', methods=['GET'])
def sysuser_add_form():
    return render_template('sysuser_add_form.html')

@app.route('/system/users/added', methods=['POST'])
def add_sysuser():
    # Picking up data from the form
    name = request.form.get('name', '').strip()
    surname = request.form.get('surname', '').strip()
    email = request.form.get('email', '').strip()
    role = request.form.get('role', 'user').strip()
    p_id = request.form.get('p_id', 'p_id').strip()
    password = request.form.get('password', '').strip()

    # checking if all requred fields are filled
    if not all([name, surname, email, password]):
        return jsonify({"error": "All fields must be filled."}), 400

    # Email format validation
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({"error": "Invalid email format."}), 400

    # Checking the passworod lenght
    if len(password) < 8:
        return jsonify({"error": "The password must be at least 8 characters long."}), 400

    # Encrypting password
    hashed_password = hashpw(password.encode('utf-8'), gensalt())

    try:
        with sqlite3.connect(SQLITE_DB) as conn:
            cursor = conn.cursor()
            sql = """
            INSERT INTO sys_usrs (email, name, surname, role, passwd, p_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            values = (email, name, surname, role, hashed_password, p_id)
            cursor.execute(sql, values)
            conn.commit()

            print(f"User {name} {surname} has been added.")  # user adding confirmation

    except sqlite3.IntegrityError as e:
        print(f"Duplicate email: {e}")  # Debug: checking for duplicated emails
        return jsonify({"error": "The email already exists."}), 400

    except sqlite3.Error as e:
        logging.exception("Database error occurred")  # Database errors message
        return jsonify({"error": "There was an error while adding the data."}), 500

    return render_template('sysuser_added.html', name=name, surname=surname, email=email, role=role)

# Fuctions updating sususer details and picking up data related data form MongoDB
@app.route('/system/users/more', methods=['GET', 'POST'])
def user_more_details():
    su_id = request.form.get('su_id')

    if su_id is None:
        flash("No user id provided", "error")
        return redirect(url_for('index'))

    # Estabishing connectin with MongoDB
    try:
        mongo_client = MongoClient(MONGO_URI)
        mongo_collection = mongo_client["ssdev001"]["patient01"]

        # SQLite connection
        with sqlite3.connect(SQLITE_DB) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('SELECT "su_id", "email", "name", "surname", "role", "p_id" FROM "sys_usrs" WHERE su_id = ?', (su_id,))
            row = cursor.fetchone()

            if not row:
                flash("User not found", "error")
                return redirect(url_for('index'))

            user_data = dict(row)
            p_id = user_data.get("p_id")

            if p_id:
                # Mapping data form MongoDB for realted SQLite user is
                mongo_field_mapping = {
                    "id": "p_id",
                    "gender": "gender",
                    "age": "age",
                    "hypertension": "has_hypertension",
                    "heart_disease": "has_heart_disease",
                    "ever_married": "marital_status",
                    "work_type": "work_type",
                    "Residence_type": "residence_type",
                    "avg_glucose_level": "avg_glucose_level",
                    "bmi": "bmi",
                    "smoking_status": "smoking_status",
                    "stroke": "stroke_history"
                }

                mongo_data = mongo_collection.find_one({"id": p_id}, {"_id": 0})
                if mongo_data:
                    mapped_data = {mongo_field_mapping[key]: value for key, value in mongo_data.items() if key in mongo_field_mapping}
                    user_data.update(mapped_data)

        return render_template('sysuser_mod_form.html', row=user_data)

    except Exception as e:
        flash(f"Error: {str(e)}", "error")
        return redirect(url_for('index'))

# SysUser updadt pasword function
@app.route('/system/users/update_pwd', methods=['POST'])
def update_password():
    pwd1 = request.form.get('pwd1')
    pwd2 = request.form.get('pwd2')
    su_id = request.form.get('su_id')

    # Matiching passwords
    if pwd1 != pwd2:
        # Flash message if passwords missmatch
        flash("Passwords do not match. Please try again.", "error")
        return redirect(url_for('index'))

    # Encrypting paswords
    hashed_pwd = hashpw(pwd1.encode('utf-8'), gensalt())

    with sqlite3.connect(SQLITE_DB) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE sys_usrs SET passwd = ? WHERE su_id = ?", (hashed_pwd, su_id))
            conn.commit()
            flash("Password updated successfully.", "success")  # Flash message - passwodr update success
        except sqlite3.Error as e:
            flash(f"An error occurred: {e}", "error")
            return redirect(url_for('index'))

    return redirect(url_for('index'))

### Patients area ####
# Liting patients form MongoDB

@app.route('/patients')
def patients():
    try:
        # Patient data pagination
        page = int(request.args.get('page', 1))  # Domyślna wartość to 1
        per_page = 20  # Liczba rekordów na stronę

        # MongoDB connection
        mongo_client = MongoClient(MONGO_URI)
        db = mongo_client["ssdev001"]
        collection = db["patient01"]

        # Data listing
        data = list(collection.find())
        for doc in data:
            doc['_id'] = str(doc['_id'])  # Zamiana ObjectId na string

        mongo_client.close()

        # Data convertion, assingling to the relevant columns
        if data:
            df = pd.DataFrame(data)
            columns_to_display = ['id', 'gender', 'age', 'work_type', 'Residence_type', 'bmi', 'smoking_status', 'stroke']
            df = df[columns_to_display]

            # Converting defoult row headers to names
            column_headers = {
                'id': 'Patient ID',
                'gender': 'Gender',
                'age': 'Age',
                'work_type': 'Work Type',
                'Residence_type': 'Residence Type',
                'bmi': 'BMI',
                'smoking_status': 'Smoking Status',
                'stroke': 'Stroke'
            }

            headers = [column_headers[col] for col in columns_to_display]

            total_records = len(df)
            total_pages = (total_records + per_page - 1) // per_page  # Liczba stron

            # Pagination
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            df_page = df.iloc[start_idx:end_idx]

            users_data = df_page.to_dict(orient='records')
        else:
            users_data = []
            total_pages = 1

        # Passing data to the html template
        return render_template(
            'patients.html',
            users_data=users_data,
            page=page,
            total_pages=total_pages,
            headers=headers,
            columns=columns_to_display
        )

    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/patient_details/<patient_id>')
def patient_details(patient_id):
    try:
        # ModogoDB connectin
        mongo_client = MongoClient(MONGO_URI)
        db = mongo_client["ssdev001"]
        collection = db["patient01"]

        # Converting p_id form string to numbaer
        try:
            patient_id = int(patient_id)
        except ValueError:
            return "Invalid patient ID", 400

        # Picking up the daa for MongoDB besed on patient id not document _id
        patient_data = collection.find_one({'id': patient_id})

        mongo_client.close()

        if patient_data:
            # remówing _id field from displaing
            patient_data.pop('_id', None)

            return render_template('patient_details.html', patient=patient_data)
        else:
            return "Patient not found", 404

    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/patient_register')
def patient_register():
    return render_template('patient_rform.html')

# MongoDB connection test
@app.route('/mongo_test')
def mongo_test():

    try:
        mongo_client = MongoClient(MONGO_URI)
        db = mongo_client["ssdev001"]
        collection = db["patient01"]

        data = list(collection.find())
        for doc in data:
            doc['_id'] = str(doc['_id'])

        mongo_client.close()

        return f"<pre>{data}</pre>"

    except Exception as e:

        return f"Error: {str(e)}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=True, use_reloader=False)
