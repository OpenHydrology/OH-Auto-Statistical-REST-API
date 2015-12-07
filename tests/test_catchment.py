import unittest
import core
import flask


class CatchmentTestCase(unittest.TestCase):
    API_URL = '/api/v0'

    def setUp(self):
        self.flask_app = core.app.flask_app.test_client()

    def test_single_catchment(self):
        resp = self.flask_app.get(self.API_URL + '/catchments/3002')
        data = flask.json.loads(resp.get_data())
        self.assertEqual(data['id'], 3002)

    def test_non_existent_catchment(self):
        resp = self.flask_app.get(self.API_URL + '/catchments/9999')
        self.assertEqual(resp.status_code, 404)

    def test_non_numeric_catchment_id(self):
        resp = self.flask_app.get(self.API_URL + '/catchments/abc')
        self.assertEqual(resp.status_code, 404)

    def test_catchment_list(self):
        resp = self.flask_app.get(self.API_URL + '/catchments/')
        data = flask.json.loads(resp.get_data())
        self.assertGreater(len(data), 0)  # Must be a list
        self.assertGreater(data[0]['id'], 2000)  # Just check for first catchment id
