import unittest
from app import app
import re

class TestAddSysUser(unittest.TestCase):
    def setUp(self):

        self.app = app
        self.client = app.test_client()
        self.app.testing = True

    # creating and adding new testing user
    def test_add_user_success(self):
        """User adding testing"""
        data = {
            "name": "John",
            "surname": "Doe",
            "email": "john.doe@example.com",
            "password": "securepassword123",
            "role": "admin"
        }
        # there will be an testing error messege if testing user aready exist
        response = self.client.post('/system/users/added', data=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"User John Doe has been add.", response.data)

    # testing for all fields fulfilled
    def test_missing_fields(self):
        """All fields filled testing"""
        data = {
            "name": "John",
            # Missing surname, email, password
        }
        response = self.client.post('/system/users/added', data=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"All fields must be filled.", response.data)

    # testing for correct email format  - containing '@'
    def test_invalid_email_format(self):
        """Correct email testing"""
        data = {
            "name": "John",
            "surname": "Doe",
            "email": "invalid_email",
            "password": "securepassword123",
            "role": "user"
        }
        response = self.client.post('/system/users/added', data=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Invalid email format.", response.data)

    # testing password length for 8 characters long
    def test_short_password(self):
        """Password length testing"""
        data = {
            "name": "John",
            "surname": "Doe",
            "email": "john.doe@example.com",
            "password": "short",
            "role": "user"
        }
        response = self.client.post('/system/users/added', data=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"The password must be at least 8 characters long.", response.data)

    # testing for duplicat email address
    def test_duplicate_email(self):
        """Duplicate email testing"""
        data = {
            "name": "John",
            "surname": "Doe",
            "email": "duplicate@example.com",
            "password": "securepassword123",
            "role": "user"
        }
        # Adding new user first time
        self.client.post('/system/users/added', data=data)

        # trying to add user with duplicated email
        response = self.client.post('/system/users/added', data=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"The email already exists.", response.data)

    # testing for database errrors messages 
    def test_database_error(self):
        """Database errors testing"""
        # Database error simulation
        with app.app_context():
            with app.test_request_context():
                response = self.client.post('/system/users/added', data={
                    "name": "Jane",
                    "surname": "Doe",
                    "email": "jane.doe@example.com",
                    "password": "securepassword123",
                    "role": "admin"
                })
                self.assertEqual(response.status_code, 400)
                self.assertIn(b"The email already exists", response.data)

if __name__ == '__main__':
    unittest.main()
