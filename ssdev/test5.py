import unittest
from flask import Flask
from app import app

### Flash messages unittest

class TestUpdatePassword(unittest.TestCase):
    def setUp(self):

        self.app = app.test_client()
        self.app.testing = True

    def test_passwords_do_not_match(self):
        # Messeg on password missmatch
        # setting up post data
        response = self.app.post('/system/users/update_pwd', data={
            'pwd1': 'password123',
            'pwd2': 'differentPassword123',
            'su_id': '1'
        }, follow_redirects=True)

        # Chcecking if messege comes up
        self.assertIn(b"Passwords do not match. Please try again.", response.data)

    def test_password_updated_successfully(self):
        # Testing pssword update
        # setting up post data
        response = self.app.post('/system/users/update_pwd', data={
            'pwd1': 'password123',
            'pwd2': 'password123',
            'su_id': '1'
        }, follow_redirects=True)

        # checking flash message on password update
        self.assertIn(b"Password updated successfully.", response.data)

if __name__ == '__main__':
    unittest.main()
