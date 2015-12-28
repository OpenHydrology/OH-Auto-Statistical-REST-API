# -*- coding: utf-8 -*-

import sys

import os
from datetime import date


os.chdir('../..')  # Versioneer requires us to work from the root of the project
sys.path.insert(0, os.getcwd())
import versioneer

extensions = ['sphinxcontrib.httpdomain']

needs_sphinx = '1.3'
templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'

project = 'OH Auto Statistical REST API'
copyright = '2015‒{}, Florenz A. P. Hollebrandse'.format(date.today().year)
release = versioneer.get_version()
version = '.'.join(release.split('.')[:2])

highlight_language = 'json'
primary_domain = 'http'
pygments_style = 'sphinx'

on_rtd = os.environ.get('READTHEDOCS', None) == 'True'
if not on_rtd:  # only import and set the theme if we're building docs locally
    import sphinx_rtd_theme

    html_theme = 'sphinx_rtd_theme'
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

html_title = ''
html_static_path = ['_static']
html_last_updated_fmt = '%d/%m/%Y'
html_show_sphinx = False
htmlhelp_basename = 'doc'
html_show_sourcelink = False
