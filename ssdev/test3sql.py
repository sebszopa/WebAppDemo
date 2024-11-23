import unittest
from flask import Flask, render_template

app = Flask(__name__)

# Hone Page

class TestUserExists(unittest.TestCase):
    def setUp(self):
        self.name = 'jan'
        self.email = 'kowalski@com'

        #test - chceking if template is  correctly rendered
        # testing is website alive - return code 200
        # testing if temlate elemetnts are correctly included and page title is diplayed

    def test_user_exists(self):

        self.assertIn(b"<title>Test App SSDev</title>", response.data)

        # test - chcecking if the systemusers page is displaing

    def test_systempage_response(self):
            response = self.client.get('/system', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"<h1>System Users</h1>", response.data)

unittest.main(argv=[''], verbosity=2, exit=False)
