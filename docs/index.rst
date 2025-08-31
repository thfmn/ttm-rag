Welcome to Thai Traditional Medicine RAG Bot
============================================

Production-grade, joyful, cookbook-first documentation for a high-stakes RAG system. Learn fast, build confidently, and ship reliably with best-practice patterns from Sphinx, Pydantic v2, FastAPI, and Pydantic-AI.

.. admonition:: 10-minute Quickstart (Docs)
   :class: tip

   1) Install doc dependencies (one time, using uv):

      .. code-block:: bash

         uv pip install sphinx myst-parser furo sphinx-design sphinx-copybutton sphinx-autodoc-typehints sphinx-sitemap sphinxext-opengraph sphinxcontrib-mermaid linkify-it-py sphinx-autobuild

   2) Build docs:

      .. code-block:: bash

         uv run sphinx-build -b html docs docs/_build/html

   3) Serve locally (option A: fast reload):

      .. code-block:: bash

         uv run sphinx-autobuild -b html docs docs/_build/html

      Option B (script if available):

      .. code-block:: bash

         uv run python serve_docs.py

.. grid:: 1 1 2 3
   :gutter: 2

   .. card:: Tutorials
      :link: tutorials/index
      :text-align: center
      :class-card: sd-shadow-sm sd-rounded-1

      Step-by-step guides from zero to working.

   .. card:: How-to Guides
      :link: how-to/index
      :text-align: center
      :class-card: sd-shadow-sm sd-rounded-1

      Task-focused cookbooks to get things done.

   .. card:: Reference
      :link: reference/index
      :text-align: center
      :class-card: sd-shadow-sm sd-rounded-1

      API docs, configuration, and data models.

   .. card:: Explanations
      :link: explanations/index
      :text-align: center
      :class-card: sd-shadow-sm sd-rounded-1

      Architecture, design decisions, testing strategy.

   .. card:: API (autosummary)
      :link: api/index
      :text-align: center
      :class-card: sd-shadow-sm sd-rounded-1

      Auto-generated API reference from source code.

.. note::

   Looking for the original pages? We&#39;re migrating to a cookbook-first structure.
   The existing content is still available and linked from the section landing pages.

.. toctree::
   :hidden:
   :maxdepth: 2

   getting-started/index
   tutorials/index
   how-to/index
   reference/index
   explanations/index
   api/index
