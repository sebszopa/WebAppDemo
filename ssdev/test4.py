from flask import Flask, render_template
import unittest
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


class TestIndex(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = app.test_client()

        #test - chceking if template is  correctly rendered
        # testing is website alive - return code 200
        # testing if temlate elemetnts are correctly included and page title is diplayed

    def test_homepage_response(self):
        response = self.client.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"<title>Test App SSDev</title>", response.data)

        # test - chcecking if the systemusers page is displaing

    def test_systempage_response(self):
            response = self.client.get('/system', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"<h1>System Users</h1>", response.data)

    # test to check displaing the system user add form page.

    def test_sys_user_add_response(self):
                response = self.client.get('/system/users/add', follow_redirects=True)
                self.assertEqual(response.status_code, 200)
                self.assertIn(b"<h1>System User Add Form</h1>", response.data)

unittest.main(argv=[''], verbosity=2, exit=False)
