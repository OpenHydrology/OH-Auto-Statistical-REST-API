import unittest
import tasks


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

    @unittest.skip
    def test_data_import(self):
        url = 'https://github.com/OpenHydrology/flood-data/archive/master.zip'
        tasks.import_data(url)
