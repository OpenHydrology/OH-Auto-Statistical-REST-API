import unittest
import autostatisticalweb as aw
import datetime
import os.path
import floodestimation.parsers
import core


class AutoStatisticalTestCase(unittest.TestCase):
    """
    Fairly simplistic testing just to make sure we don't break the analyses. The floodestimation library is extensively
    unit-tested so we should be reasonably ok.
    """
    @classmethod
    def setUpClass(cls):
        cls.catchment = floodestimation.parsers.Cd3Parser().parse('tests/data/8002.CD3')
        cls.db_session = core.db.Session()

    def test_analysis_setup(self):
        a = aw.Analysis(self.catchment, self.db_session)
        self.assertIsNone(a.gauged_catchments)
        self.assertEqual(a.results, {})
        self.assertIsNone(a.qmed)

    def test_analysis_run(self):
        a = aw.Analysis(self.catchment, self.db_session)
        r = a.run()
        self.assertTrue(r.startswith("# Flood Estimation Report"))

    def test_analysis_run_qmed(self):
        a = aw.Analysis(self.catchment, self.db_session)
        a._run_qmed_analysis()
        self.assertEqual(a.results['qmed']['method'], 'descriptors')  # ungauged analysis
        self.assertGreater(a.qmed, 0)
        self.assertLess(a.qmed, 1000)  # just test for realistic range
        self.assertEqual(a.qmed, a.results['qmed']['qmed_descr_urban'])
        self.assertLessEqual(a.results['qmed']['qmed_descr_rural'],
                             a.results['qmed']['qmed_descr_urban'])

    def test_analysis_run_growthcurve(self):
        a = aw.Analysis(self.catchment, self.db_session)
        a.qmed = 10
        a._load_data()
        a._run_growthcurve()
        self.assertEqual(a.qmed, a.results['gc']['flows'][0])
        self.assertEqual(a.results['gc']['growth_factors'][0], 1)
        self.assertTrue(all(gf >= 1 for gf in a.results['gc']['growth_factors']))
        self.assertLess(a.results['gc']['growth_factors'][-1], 9)  # just test for realistic range


class ReportTestCase(unittest.TestCase):
    def test_report_setup(self):
        r = aw.Report({}, 'normal.md')
        self.assertEqual(r.template.name, 'normal.md')

    def test_report_get_content(self):
        # minimum dummy context to be able to render template
        empty_context = {'catchment': {'point': {}, 'descriptors': {'centroid_ngr': {}}},
                         'nrfa': {},
                         'qmed': {},
                         'gc': {'distr_params': {}}}
        r = aw.Report(empty_context, 'normal.md')
        c = r.get_content()
        self.assertTrue(c.startswith("# Flood Estimation Report"))
        self.assertTrue(c.endswith("Open Hydrology Contributors (2015). OH Auto Statistical. "
                                   "http://docs.open-hydrology.org/projects/oh-auto-statistical"))


class TemplateEnvironmentTestCase(unittest.TestCase):
    TE = aw.TemplateEnvironment

    def test_find_normal_template(self):
        te = self.TE()
        template = te.get_template('normal.md')
        self.assertEqual(template.name, 'normal.md')
        self.assertEqual(template.filename, os.path.abspath(os.path.join('templates', 'normal.md')))

    def test_filters_setup(self):
        expected_filers = ['dateformat', 'intcolumn', 'round', 'floatcolumn', 'signif', 'signifcolumn', 'intcolumn',
                           'strcolumn', 'default']
        actual_filters = self.TE().filters.keys()
        self.assertTrue(set(expected_filers).issubset(set(actual_filters)))

    def test_dateformat_default(self):
        s = self.TE.dateformat(datetime.date(2000, 1, 31))
        self.assertEqual(s, '31/01/2000')

    def test_dateformat_custom(self):
        s = self.TE.dateformat(datetime.date(2000, 1, 31), format='%Y-%m-%d')
        self.assertEqual(s, '2000-01-31')

    def test_dateformat_non_date(self):
        s = self.TE.dateformat(None)
        self.assertEqual(s, '')

    def test_round_default(self):
        s = self.TE.round(1.234)
        self.assertEqual(s, '1.23')

    def test_round_custom(self):
        s = self.TE.round(1.01, decimals=1)
        self.assertEqual(s, '1.0')

    def test_round_non_numeric(self):
        s = self.TE.round(None)
        self.assertEqual(s, '')

    def test_float_column_default(self):
        s = self.TE.floatcolumn(1.2)
        self.assertEqual(s, '       1.200')

    def test_float_column_decimals(self):
        s = self.TE.floatcolumn(1.26, decimals=1)
        self.assertEqual(s, '         1.3')

    def test_float_column_width(self):
        s = self.TE.floatcolumn(1.2, width=10)
        self.assertEqual(s, '     1.200')

    def test_float_column_separator_position(self):
        s = self.TE.floatcolumn(1.2, sep_pos=3)
        self.assertEqual(s, ' 1.200\u2007\u2007\u2007\u2007\u2007\u2007')

    def test_float_column_zero_decimals(self):
        s = self.TE.floatcolumn(1.2, decimals=0)
        self.assertEqual(s, '          1\u2008')

    def test_signif_default(self):
        s = self.TE.signif(1.23)
        self.assertEqual(s, '1.2')

    def test_signif_default_small_number(self):
        s = self.TE.signif(0.00123)
        self.assertEqual(s, '0.0012')

    def test_signif_default_large_number(self):
        s = self.TE.signif(12345)
        self.assertEqual(s, '12000')

    def test_signif_significance(self):
        s = self.TE.signif(1.23, significance=4)
        self.assertEqual(s, '1.230')

    def test_signif_non_numeric(self):
        s = self.TE.signif(None)
        self.assertEqual(s, '')

    def test_signifcolumn_default(self):
        s = self.TE.signifcolumn(1.23)
        self.assertEqual(s, '         1.2')

    def test_signifcolumn_signficance(self):
        s = self.TE.signifcolumn(1.23, significance=3)
        self.assertEqual(s, '        1.23')

    def test_signifcolumn_width(self):
        s = self.TE.signifcolumn(1.23, width=8)
        self.assertEqual(s, '     1.2')

    def test_signifcolumn_separator_position(self):
        s = self.TE.signifcolumn(1.23, sep_pos=6)
        self.assertEqual(s, '    1.2\u2007\u2007\u2007\u2007\u2007')

    def test_intcolumn_default(self):
        s = self.TE.intcolumn(123)
        self.assertEqual(s, '         123')

    def test_intcolumn_width(self):
        s = self.TE.intcolumn(123, width=6)
        self.assertEqual(s, '   123')

    def test_intcolumn_non_integer(self):
        s = self.TE.intcolumn(1.23)
        self.assertEqual(s, '           1')

    def test_intcolumn_non_numeric(self):
        s = self.TE.intcolumn(None)
        self.assertEqual(s, '            ')

    def test_strcolumn_default(self):
        s = self.TE.strcolumn('bla')
        self.assertEqual(s, 'bla                      ')

    def test_strcolumn_width(self):
        s = self.TE.strcolumn('bla', width=6)
        self.assertEqual(s, 'bla   ')

    def test_strcolumn_too_narrow(self):
        # Will overflow
        s = self.TE.strcolumn('bla', width=2)
        self.assertEqual(s, 'bla')

    def test_strcolumn_non_string(self):
        s = self.TE.strcolumn(None)
        self.assertEqual(s, '                         ')

    def test_default_default(self):
        s = self.TE.default(None)
        self.assertEqual(s, '')

    def test_default_custom(self):
        s = self.TE.default(None, 'bla')
        self.assertEqual(s, 'bla')

    def test_default_value_provided(self):
        s = self.TE.default('bla', default='bla bla')
        self.assertEqual(s, 'bla')
