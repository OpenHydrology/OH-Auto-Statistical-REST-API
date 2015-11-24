# -*- coding: utf-8 -*-

import os.path
from datetime import date
from floodestimation.collections import CatchmentCollections
from floodestimation.analysis import QmedAnalysis, GrowthCurveAnalysis
import math
import jinja2 as jj
import jinja2.exceptions
import jinja2.utils


class Analysis(object):
    """
    Analysis and report creation object.

    """
    def __init__(self, catchment, db_session):
        #: :class:`floodestimation.entities.Catchment` object
        self.catchment = catchment
        #: Database session
        self.db_session = db_session
        #: Gauged catchments collection
        self.gauged_catchments = None
        #: Big dict holding all results, to be passed as context to Jinja2
        self.results = {}
        #: QMED result value
        self.qmed = None
        #: Any exceptions occurring during analysis
        self.exc = None

    def _load_data(self):
        self.results['report_date'] = date.today()
        self.results['version'] = '0.0.0'
        self.results['catchment'] = self.catchment
        self.gauged_catchments = CatchmentCollections(self.db_session, load_data='manual')

    def run(self):
        self._load_data()
        self._run_qmed_analysis()
        self._run_growthcurve()
        return self._create_report()

    def _run_qmed_analysis(self):
        results = {}

        analysis = QmedAnalysis(self.catchment, self.gauged_catchments, results_log=results)
        self.qmed = analysis.qmed()

        results['qmed'] = self.qmed
        self.results['qmed'] = results

    def _run_growthcurve(self):
        results = {}

        analysis = GrowthCurveAnalysis(self.catchment, self.gauged_catchments, results_log=results)
        gc = analysis.growth_curve()

        aeps = [0.5, 0.2, 0.1, 0.05, 0.03333, 0.02, 0.01333, 0.01, 0.005, 0.002, 0.001]
        growth_factors = gc(aeps)
        flows = growth_factors * self.qmed

        results['aeps'] = aeps
        results['growth_factors'] = growth_factors
        results['flows'] = flows
        self.results['gc'] = results

    def _create_report(self):
        rep = Report(self.results, template_name='normal.md')
        return rep.get_content()


class Report(object):
    def __init__(self, context, template_name):
        self.context = context
        self.template_name = template_name
        self.template_extension = os.path.splitext(template_name)[1]
        self.template = self._get_template()

    def _get_template(self):
        env = TemplateEnvironment()
        return env.get_template(self.template_name)

    def get_content(self):
        return self.template.render(self.context)


class TemplateEnvironment(jj.Environment):
    """
    A jinja2 template environment with loader and filters setup.
    """
    def __init__(self):
        jj.Environment.__init__(self)
        self.trim_blocks = True

        # Load templates from within the package
        self.loader = jj.ChoiceLoader([
            jj.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates'))
        ])

        # Custom formatting filters
        self.filters['dateformat'] = self.dateformat
        self.filters['round'] = self.round
        self.filters['signif'] = self.signif
        self.filters['floatcolumn'] = self.floatcolumn
        self.filters['signifcolumn'] = self.signifcolumn
        self.filters['intcolumn'] = self.intcolumn
        self.filters['strcolumn'] = self.strcolumn
        self.filters['default'] = self.default

    @staticmethod
    def dateformat(value, format='%d/%m/%Y'):
        """
        Format a date
        """
        try:
            return value.strftime(format)
        except (ValueError, TypeError, AttributeError, jinja2.exceptions.UndefinedError):
            return ""

    @staticmethod
    def round(value, decimals=2):
        """
        Override the default jinja round filter as it drops decimals.
        """
        try:
            return "{value:.{decimals:d}f}".format(value=value, decimals=decimals)
        except (ValueError, TypeError):
            return ""

    @staticmethod
    def floatcolumn(value, decimals=3, width=12, sep_pos=None):
        """
        Format number within a fixed-width column and specified number of decimal places.

        The formatter assumes columns are right-aligned: padding to the left of the value are ordinary spaces (which may
        collapse in HTML) and padding to the right are figure spaces (they have the same width as numerals in non
        fixed-width fonts, they don't collapse in HTML). Some fixed-width fonts actually adjust the width of figure
        spaces and punctuation spaces, which is silly.

        :param value: Value to be formatted
        :param decimals: Number of decimal places, default: 3
        :param width: Column width, default: 12 characters
        :param sep_pos: Position of the decimal point within the column
        :return: Formatted string
        """
        if not sep_pos:
            sep_pos = width - decimals
        number_width = sep_pos + decimals
        if decimals == 0:
            number_width -= 1
            padding = ' ' + ' ' * (width - number_width - 1)  # punctuation space followed by figure spaces
        else:
            padding = ' ' * (width - number_width)  # figure spaces
        try:
            return "{value:>{width:d}.{decimals:d}f}{padding:s}". \
                format(value=value, width=number_width, decimals=decimals, padding=padding)
        except (ValueError, TypeError):
            return ' ' * (sep_pos - 1) + ' ' + ' ' * (width - sep_pos)

    @staticmethod
    def signif(value, significance=2):
        """
        Format a float with a certain number of significant figures.

        E.g.:

            signif(1.234) == '1.23'
            signif(123.4) == '120'

        :param value: Value to be formatted
        :param significance: Number of significant figures
        :return: Formatted string
        """
        try:
            order = math.floor(math.log10(value))
            decimals = max(0, significance - order - 1)
            rounded_value = round(value, significance - order - 1)
            return "{value:.{decimals:d}f}".format(value=rounded_value, decimals=decimals)
        except (ValueError, TypeError, jinja2.exceptions.UndefinedError):
            return ""

    @staticmethod
    def signifcolumn(value, significance=2, width=12, sep_pos=None):
        """
        Formats a floating point number within fixed-with column using specified significant digits

        :param value: numeric value to be formatted
        :param significance: number of significant digits, default: 2 digits
        :param width: Column width, default: 12 characters
        :param sep_pos: Position of the decimal point within the column
        :return: Formatted string
        """
        order = math.floor(math.log10(value))
        decimals = max(0, significance - order - 1)
        rounded_value = round(value, significance - order - 1)
        return TemplateEnvironment.floatcolumn(rounded_value, decimals, width, sep_pos)

    @staticmethod
    def intcolumn(value, width=12):
        """
        Formats an integer within fixed-with column, right-aligned

        :param value: integer value to be formatted
        :param width: Column width, default: 12 characters
        :return: Formatted string
        """
        try:
            return "{value:>{width:d}.0f}".format(value=value, width=width)
        except (ValueError, TypeError):
            return ' ' * width

    @staticmethod
    def strcolumn(value, width=25):
        """
        Formats a string within fixed-with column, left-aligned

        :param value: string value to be formatted
        :param width: Column width, default: 25 characters
        :return: Formatted string
        """
        try:
            return "{value:<{width:d}s}".format(value=value, width=width)
        except (ValueError, TypeError):
            return ' ' * width

    @staticmethod
    def default(value, default=''):
        if value is None or jinja2.utils.is_undefined(value):
            return default
        else:
            return value
