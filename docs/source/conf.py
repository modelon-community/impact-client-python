# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import subprocess
import sys

import sphinx_rtd_theme

sys.path.insert(0, os.path.abspath("../.."))

# -- Project information -----------------------------------------------------

project = "Modelon-impact-client"
copyright = "2020-2024, Modelon"
author = "Modelon"

# The full version, including alpha/beta/rc tags
release = subprocess.check_output(["poetry", "version", "-s"])[:-1].decode()
master_doc = "index"

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx_rtd_theme",
    "sphinx_copybutton",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.napoleon",
    "sphinxcontrib.spelling",
    "sphinx_search.extension",
    "sphinx_autodoc_typehints",
]

add_module_names = False

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

html_theme_options = {
    "style_nav_header_background": "#fb8c00",
}

# The wordlist with known words, like Jupyterlab
spelling_word_list_filename = "spelling_wordlist.txt"
spelling_show_suggestions = True
spelling_ignore_acronyms = True
spelling_exclude_patterns = ["modelon.*"]

# Enable google style docstrings
napoleon_google_docstring = True


# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
html_css_files = ["custom.css"]

suppress_warnings = [
    "autosectionlabel.*"
]  # See https://github.com/sphinx-doc/sphinx/issues/7697
