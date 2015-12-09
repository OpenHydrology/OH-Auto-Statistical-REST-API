import unittest
import flask
import core
import tasks
from unittest import mock


@mock.patch.object(tasks.do_analysis_from_id, 'run', autospec=True)
@mock.patch.object(tasks.do_analysis, 'run', autospec=True)
class AnalysisTestCase(unittest.TestCase):
    API_URL = '/api/v0'

    @classmethod
    def setUpClass(cls):
        core.celery.conf['CELERY_ALWAYS_EAGER'] = True

    def setUp(self):
        self.test_client = core.app.flask_app.test_client()

    def test_no_data(self, do_analysis, do_analysis_from_id):
        resp = self.test_client.post(self.API_URL + '/analyses/')
        data = flask.json.loads(resp.get_data())
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(data['message'], "Catchment file (.cd3 or .xml) required.")

    def test_catchment_id_only(self, do_analysis, do_analysis_from_id):
        form_data = {'nrfa-id': 3002}
        resp = self.test_client.post(self.API_URL + '/analyses/', data=form_data)
        self.assertEqual(resp.status_code, 202)
        self.assertIn(self.API_URL + '/analysis-tasks/', resp.headers['Location'])
        do_analysis_from_id.assert_called_with(3002)

    def test_non_cd3_file(self, do_analysis, do_analysis_from_id):
        form_data = {'file': (open('tests/data/8002.CD3', 'rb'), '8002.bla')}
        resp = self.test_client.post(self.API_URL + '/analyses/', data=form_data)
        data = flask.json.loads(resp.get_data())
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(data['message'], "Catchment file (.cd3 or .xml) required.")

    def test_cd3_plus_non_am_file(self, do_analysis, do_analysis_from_id):
        form_data = {'file1': (open('tests/data/8002.CD3', 'rb'), '8002.CD3'),
                     'file2': (open('tests/data/8002.AM', 'rb'), '8002.bla')}
        resp = self.test_client.post(self.API_URL + '/analyses/', data=form_data)
        data = flask.json.loads(resp.get_data())
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(data['message'], "Second file must be AMAX (.am) file.")

    def test_too_many_files(self, do_analysis, do_analysis_from_id):
        form_data = {'file1': (open('tests/data/8002.CD3', 'rb'), '8002.CD3'),
                     'file2': (open('tests/data/8002.AM', 'rb'), '8002.am'),
                     'file3': (open('tests/data/8002.AM', 'rb'), '8002.bla')}
        resp = self.test_client.post(self.API_URL + '/analyses/', data=form_data)
        data = flask.json.loads(resp.get_data())
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(data['message'], "Too many files supplied.")

    def test_cd3_file_only(self, do_analysis, do_analysis_from_id):
        with open('tests/data/8002.CD3', 'r') as cd3_f:
            cd3_content = cd3_f.read()
        form_data = {'file': (open('tests/data/8002.CD3', 'rb'), '8002.CD3')}
        resp = self.test_client.post(self.API_URL + '/analyses/', data=form_data)
        self.assertEqual(resp.status_code, 202)
        self.assertIn(self.API_URL + '/analysis-tasks/', resp.headers['Location'])
        do_analysis.assert_called_with(cd3_content, amax_str=None)

    def test_cd3_and_am_file(self, do_analysis, do_analysis_from_id):
        with open('tests/data/8002.CD3', 'r') as cd3_f:
            cd3_content = cd3_f.read()
        with open('tests/data/8002.AM', 'r') as am_f:
            am_content = am_f.read()
        form_data = {'file1': (open('tests/data/8002.CD3', 'rb'), '8002.CD3'),
                     'file2': (open('tests/data/8002.AM', 'rb'), '8002.AM')}
        resp = self.test_client.post(self.API_URL + '/analyses/', data=form_data)
        self.assertEqual(resp.status_code, 202)
        self.assertIn(self.API_URL + '/analysis-tasks/', resp.headers['Location'])
        do_analysis.assert_called_with(cd3_content, amax_str=am_content)

    def test_get_non_existent_analysis(self, do_analysis, do_analysis_from_id):
        resp = self.test_client.get(self.API_URL + '/analyses/bla')
        data = flask.json.loads(resp.get_data())
        self.assertEqual(resp.status_code, 404)
        self.assertTrue(data['message'].startswith("Analysis does not exist."))
