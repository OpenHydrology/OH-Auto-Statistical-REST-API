import unittest
from unittest import mock
import tasks
import urllib.request
import urllib.parse
import os.path
import requests


class TestTasks(unittest.TestCase):
    def test_do_analysis(self):
        catchment_str = open('tests/data/8002.CD3').read()
        r = tasks.do_analysis(catchment_str)
        self.assertTrue(r['result'].startswith("# Flood Estimation Report"))
        self.assertIn("Catchment descriptors regression model with nearby catchments adjustment", r['result'])

    def test_do_analysis_with_am(self):
        catchment_str = open('tests/data/8002.CD3').read()
        amax_str = open('tests/data/8002.AM').read()
        r = tasks.do_analysis(catchment_str, amax_str)
        self.assertTrue(r['result'].startswith("# Flood Estimation Report"))
        self.assertIn("Median of annual maximum flow data", r['result'])

    def test_do_analysis_xml_catchment(self):
        catchment_str = open('tests/data/catchment.xml').read()
        r = tasks.do_analysis(catchment_str)
        self.assertTrue(r['result'].startswith("# Flood Estimation Report"))
        self.assertIn("Catchment descriptors regression model with nearby catchments adjustment", r['result'])

    def test_do_analysis_from_id(self):
        r = tasks.do_analysis_from_id(3002)
        self.assertTrue(r['result'].startswith("# Flood Estimation Report"))
        self.assertIn("Median of annual maximum flow data", r['result'])

    def test_do_analysis_from_id_non_existent_id(self):
        self.assertRaises(ValueError, tasks.do_analysis_from_id, 1000)

    def test_is_xml_true(self):
        catchment_str = open('tests/data/catchment.xml').read()
        self.assertTrue(tasks.is_xml(catchment_str))

    def test_data_import(self):
        # We need to patch requests, because it doesn't support `file:///`
        s = requests.session()
        s.mount('file://', LocalFileAdapter())
        with mock.patch.object(tasks.requests, 'get', s.get):
            url = 'file:' + urllib.request.pathname2url(os.path.abspath('tests/data/data.zip'))
            tasks.import_data(url)
            # TODO: assert something!

    def test_is_xml_false(self):
        catchment_str = open('tests/data/8002.CD3').read()
        self.assertFalse(tasks.is_xml(catchment_str))


class LocalFileAdapter(requests.adapters.BaseAdapter):
    """Protocol Adapter to allow Requests to GET file:// URLs"""

    @staticmethod
    def _chkpath(method, path):
        """Return an HTTP status for the given filesystem path."""
        if method.lower() in ('put', 'delete'):
            return 501, "Not Implemented"
        elif method.lower() not in ('get', 'head'):
            return 405, "Method Not Allowed"
        elif os.path.isdir(path):
            return 400, "Path Not A File"
        elif not os.path.isfile(path):
            return 404, "File Not Found"
        elif not os.access(path, os.R_OK):
            return 403, "Access Denied"
        else:
            return 200, "OK"

    def send(self, req, **kwargs):
        """Return the file specified by the given request """
        path = os.path.normcase(os.path.normpath(urllib.request.url2pathname(req.path_url)))
        response = requests.Response()
        response.status_code, response.reason = self._chkpath(req.method, path)
        if response.status_code == 200 and req.method.lower() != 'head':
            try:
                response.raw = open(path, 'rb')
            except (OSError, IOError) as err:
                response.status_code = 500
                response.reason = str(err)

        if isinstance(req.url, bytes):
            response.url = req.url.decode('utf-8')
        else:
            response.url = req.url

        response.request = req
        response.connection = self

        return response

    def close(self):
        pass

