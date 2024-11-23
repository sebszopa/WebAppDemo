from flask import Flask, render_template
import sqlite3
import pandas as pd

# Databases connectio config file
from config import SQLITE_DB

app = Flask(__name__)

# Hone Page
@app.route('/')

# rendering idex.html as home page
# the index.html file uses includ function to dynamically create website menu and content page
# it give and option to keep the code clean and tidy

def index():
    return render_template('index.html')

# Added connection with SQLite databes
# The page list users data form SQLite databes
# by usinig SELECT function it takes specific data from Databases

@app.route('/system')
def get_sysusers():
    with sqlite3.connect(SQLITE_DB) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT "su_id", "email", "name", "surname", "role" FROM "sys_usrs";')
        rows = cursor.fetchall()

    return render_template('sysusers.html', rows=rows)

# from tu add sustem users to SQLite database

@app.route('/system/users/add')
def sysuser_add_form():
    return render_template('sysuser_add_form.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=True, use_reloader=False)
