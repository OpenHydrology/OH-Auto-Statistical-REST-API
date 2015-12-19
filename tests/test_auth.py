import unittest
import jwt
import core
import auth
import base64
from werkzeug.exceptions import Unauthorized


class AuthTestCase(unittest.TestCase):
    client_id = core.app.flask_app.config['AUTH_CLIENT_ID']
    client_secret = core.app.flask_app.config['AUTH_CLIENT_SECRET']

    def test_no_aud(self):
        payload = {
            'user_id': 0
        }
        token = jwt.encode(
            payload,
            base64.b64decode(self.client_secret.replace("_", "/").replace("-", "+"))
        )
        with self.assertRaises(Unauthorized) as cm:
            auth.authenticate_user(token)
        self.assertEqual(cm.exception.description, 'Token invalid')

    def test_invalid_aud(self):
        payload = {
            'user_id': 0,
            'aud': 'bla'
        }
        token = jwt.encode(
            payload,
            base64.b64decode(self.client_secret.replace("_", "/").replace("-", "+"))
        )
        with self.assertRaises(Unauthorized) as cm:
            auth.authenticate_user(token)
        self.assertEqual(cm.exception.description, 'Incorrect audience')

    def test_invalid_signature(self):
        payload = {
            'user_id': 0,
            'aud': self.client_id
        }
        token = jwt.encode(
            payload,
            'bla'
        )
        with self.assertRaises(Unauthorized) as cm:
            auth.authenticate_user(token)
        self.assertEqual(cm.exception.description, 'Token signature is invalid')

    def test_valid_jwt(self):
        payload = {
            'user_id': 0,
            'aud': self.client_id
        }
        token = jwt.encode(
            payload,
            base64.b64decode(self.client_secret.replace("_", "/").replace("-", "+"))
        )
        user = auth.authenticate_user(token)
        self.assertEqual(user['user_id'], 0)
