import unittest
import tasks


class TestTasks(unittest.TestCase):
    def test_data_import(self):
        url = 'https://github.com/OpenHydrology/flood-data/archive/master.zip'
        tasks.import_data(url)
