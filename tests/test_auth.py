import unittest
from datetime import datetime, timedelta
import jwt
import core
import auth
from werkzeug.exceptions import Unauthorized


class AuthTestCase(unittest.TestCase):
    client_id = core.app.flask_app.config['AUTH_CLIENT_ID']
    client_secret = core.app.flask_app.config['AUTH_CLIENT_SECRET']

    def test_no_aud(self):
        payload = {
            'user_id': 0
        }
        token = auth.create_jwt(payload, set_audience=False)
        with self.assertRaises(Unauthorized) as cm:
            auth.authenticate_user(token)
        self.assertEqual(cm.exception.description, 'Token invalid')

    def test_invalid_aud(self):
        payload = {
            'user_id': 0,
            'aud': 'bla'
        }
        token = auth.create_jwt(payload, set_audience=False)
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

    def test_expired(self):
        payload = {
            'user_id': 0,
            'exp': datetime(2000, 1, 1)
        }
        token = auth.create_jwt(payload)
        with self.assertRaises(Unauthorized) as cm:
            auth.authenticate_user(token)
        self.assertEqual(cm.exception.description, 'Token is expired')

    def test_valid_jwt(self):
        payload = {
            'user_id': 0,
            'exp': datetime.utcnow() + timedelta(days=1)
        }
        token = auth.create_jwt(payload)
        user = auth.authenticate_user(token)
        self.assertEqual(user['user_id'], 0)

    def test_valid_jwt_no_exp(self):
        payload = {
            'user_id': 0,
        }
        token = auth.create_jwt(payload)
        user = auth.authenticate_user(token)
        self.assertEqual(user['user_id'], 0)


class BearerTokenTestCase(unittest.TestCase):
    def test_no_auth_header(self):
        headers = {}
        with self.assertRaises(Unauthorized) as cm:
            auth.auth_token(headers)
        self.assertEqual(cm.exception.description, 'Authorization header is expected')

    def test_non_bearer_token(self):
        headers = {'Authorization': 'bla'}
        with self.assertRaises(Unauthorized) as cm:
            auth.auth_token(headers)
        self.assertEqual(cm.exception.description, 'Authorization header must start with Bearer')

    def test_empty_token(self):
        headers = {'Authorization': 'Bearer'}
        with self.assertRaises(Unauthorized) as cm:
            auth.auth_token(headers)
        self.assertEqual(cm.exception.description, 'Token not found')

    def test_too_many_token_parts(self):
        headers = {'Authorization': 'Bearer bla bla'}
        with self.assertRaises(Unauthorized) as cm:
            auth.auth_token(headers)
        self.assertEqual(cm.exception.description, 'Authorization header must be Bearer + \s + token')

    def test_some_token(self):
        headers = {'Authorization': 'Bearer bla'}
        token = auth.auth_token(headers)
        self.assertEqual(token, 'bla')
