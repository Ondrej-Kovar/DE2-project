# Configuration file for the Sphinx documentation builder.
import os
import sys

# Add src folder to sys.path so Sphinx autodoc can document drivers
sys.path.insert(0, os.path.abspath('../src'))

# Project information
project = 'Smart Greenhouse Monitor'
copyright = '2026, Adam Koutný, Ondřej Kovář, Richard Královský'
author = 'Adam Koutný, Ondřej Kovář, Richard Královský'
release = '1.0'

# General configuration
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# HTML output options
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
