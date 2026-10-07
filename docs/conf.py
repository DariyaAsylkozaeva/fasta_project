# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'fasta_toolkit'
copyright = '2026, Dariya'
author = 'Dariya'
release = '1.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

import os
import sys

# Sphinx должен «увидеть» fasta_toolkit.py, который лежит
# НА УРОВЕНЬ ВЫШЕ папки docs.
sys.path.insert(0, os.path.abspath('/home/user/Bioinf-seminars'))

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx_autodoc_typehints',
]

napoleon_google_docstring = True
autodoc_member_order = 'bysource'
autodoc_typehints = 'description'

html_theme = 'alabaster'

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
