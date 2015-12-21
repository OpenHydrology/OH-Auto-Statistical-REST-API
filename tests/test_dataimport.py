import unittest
import core
import flask
import tasks
from unittest import mock
import auth


@mock.patch.object(tasks.import_data, 'run', autospec=True)
class DataImportTestCase(unittest.TestCase):
    API_URL = '/api/v0'

    @classmethod
    def setUpClass(cls):
        core.celery.conf['CELERY_ALWAYS_EAGER'] = True
        payload = {
            'roles': ['importer']
        }
        cls.auth_token = auth.create_jwt(payload)

    def setUp(self):
        self.test_client = core.app.flask_app.test_client()

    def test_no_auth_header(self, import_data):
        resp = self.test_client.post(self.API_URL + '/data-imports/')
        self.assertEqual(resp.status_code, 401)
        self.assertFalse(import_data.called)

    def test_no_role(self, import_data):
        payload = {}
        auth_token = auth.create_jwt(payload)
        headers = {'Authorization': 'Bearer ' + auth_token}
        resp = self.test_client.post(self.API_URL + '/data-imports/', headers=headers)
        self.assertEqual(resp.status_code, 403)
        self.assertFalse(import_data.called)

    def test_incorrect_role(self, import_data):
        payload = {
            'roles': ['bla']
        }
        auth_token = auth.create_jwt(payload)
        headers = {'Authorization': 'Bearer ' + auth_token}
        resp = self.test_client.post(self.API_URL + '/data-imports/', headers=headers)
        self.assertEqual(resp.status_code, 403)
        self.assertFalse(import_data.called)

    def test_plain_text_body(self, import_data):
        headers = {'Authorization': 'Bearer ' + self.auth_token}
        body = "bla"
        resp = self.test_client.post(self.API_URL + '/data-imports/', headers=headers, data=body)
        data = flask.json.loads(resp.get_data())
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(data['message'], "Request data must be JSON.")
        self.assertFalse(import_data.called)

    def test_json_body_no_url(self, import_data):
        headers = {'Authorization': 'Bearer ' + self.auth_token}
        body = flask.json.dumps({'bla': 'bla'})
        resp = self.test_client.post(self.API_URL + '/data-imports/', data=body, headers=headers,
                                     content_type='application/json')
        data = flask.json.loads(resp.get_data())
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(data['message'], "JSON body must include `url` key.")
        self.assertFalse(import_data.called)

    def test_non_zip_url(self, import_data):
        headers = {'Authorization': 'Bearer ' + self.auth_token}
        body = flask.json.dumps({'url': 'https://bla.com/file.tar.gz'})
        resp = self.test_client.post(self.API_URL + '/data-imports/', data=body, headers=headers,
                                     content_type='application/json')
        data = flask.json.loads(resp.get_data())
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(data['message'],
                         "Download URL must be a .zip file. `https://bla.com/file.tar.gz` was provided.")
        self.assertFalse(import_data.called)

    def test_non_existent_zip_url(self, import_data):
        # The REST API does not check if url exists or not, so this should return 202 (Accepted)
        headers = {'Authorization': 'Bearer ' + self.auth_token}
        body = flask.json.dumps({'url': 'https://bla.com/file.zip'})
        resp = self.test_client.post(self.API_URL + '/data-imports/', data=body, headers=headers,
                                     content_type='application/json')
        self.assertEqual(resp.status_code, 202)
        import_data.assert_called_with('https://bla.com/file.zip')
