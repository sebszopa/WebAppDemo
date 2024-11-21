import unittest
from flask import Flask, render_template

app = Flask(__name__)

# Hone Page
@app.route('/')
def index():
    return render_template('index.html')

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
