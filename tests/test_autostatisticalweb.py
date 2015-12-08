import unittest
import autostatisticalweb as aw
import datetime
import os.path


class AutoStatisticalTestCase(unittest.TestCase):
    pass


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

    def test_round_default(self):
        s = self.TE.round(1.234)
        self.assertEqual(s, '1.23')

    def test_round_custom(self):
        s = self.TE.round(1.01, decimals=1)
        self.assertEqual(s, '1.0')

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

    def test_default_default(self):
        s = self.TE.default(None)
        self.assertEqual(s, '')

    def test_default_custom(self):
        s = self.TE.default(None, 'bla')
        self.assertEqual(s, 'bla')
