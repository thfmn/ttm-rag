# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# Make project sources importable for autodoc
import sys
from pathlib import Path

# Insert the project src/ path (one level up from docs/)
sys.path.insert(0, str((Path(__file__).resolve().parents[1] / "src").resolve()))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Thai Traditional Medicine RAG Bot"
copyright = "2025, Tobias Hoffmann"
author = "Tobias Hoffmann"
release = "0.1.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    # Content authoring
    "myst_parser",
    # Core Sphinx
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx.ext.duration",
    "sphinx.ext.autosectionlabel",
    # UX / Design
    "sphinx_copybutton",
    "sphinx_design",
    "sphinxcontrib.mermaid",
    # Types and API rendering
    "sphinx_autodoc_typehints",
    # SEO / Social
    "sphinxext.opengraph",
    "sphinx_sitemap",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Parse both RST and Markdown sources
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static"]
html_title = "Thai Traditional Medicine RAG Bot"

# -- Options for MyST parser -------------------------------------------------
# https://myst-parser.readthedocs.io/en/latest/configuration.html

myst_enable_extensions = [
    "amsmath",
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "html_admonition",
    "html_image",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
    "linkify",
]

# -- Autosummary / Autodoc / Napoleon / Type hints --------------------------

autosummary_generate = True
autosummary_generate_overwrite = True

autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
}

# Show type hints in the description section for readability
autodoc_typehints = "description"
# Render short type names where possible
autodoc_typehints_format = "short"

# Napoleon (Google/NumPy docstring) settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_attr_annotations = True

# -- Intersphinx -------------------------------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master", None),
    "pydantic": ("https://docs.pydantic.dev/latest/", None),
    "fastapi": ("https://fastapi.tiangolo.com/", None),
    # Uncomment if/when a public intersphinx inventory exists:
    # "pydantic_ai": ("https://ai.pydantic.dev/", None),
}

# Make section labels unique by prefixing with document path
autosectionlabel_prefix_document = True

# -- SEO / OpenGraph / Sitemap ----------------------------------------------

# IMPORTANT: Set this to your actual docs URL before publishing
html_baseurl = "https://example.com/ttm-rag-docs/"

ogp_site_url = html_baseurl
ogp_description_length = 200

html_meta = {
    "description": "Thai Traditional Medicine RAG Bot: production-grade, joyful, cookbook-first docs.",
    "keywords": "RAG, FastAPI, Pydantic, Pydantic-AI, Thai Traditional Medicine, AI, ML Engineering",
}
