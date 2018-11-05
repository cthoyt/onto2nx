onto2nx |build| |coverage| |zenodo|
===================================
Converts OWL ontologies and OBO to NetworkX Graphs.

As of its first version, ``onto2nx`` currently relies on the code of a stripped-down version of
`OntoSpy <https://github.com/lambdamusic/Ontospy>`_. We would like to give a huge thank you to
`Michele Pasin <https://github.com/lambdamusic>`_ for all of his hard work and making it available under the
GPL 3.0 license so we could use it too.

Installation |python_versions| |pypi_version| |pypi_license|
------------------------------------------------------------
PyBEL can be installed easily from `PyPI <https://pypi.python.org/pypi/onto2nx>`_ with the following code in
your favorite terminal:

.. code-block:: sh

    $ python3 -m pip install onto2nx

or from the latest code on `GitHub <https://github.com/cthoyt/onto2nx>`_ with:

.. code-block:: sh

    $ python3 -m pip install git+https://github.com/cthoyt/onto2nx.git

.. |build| image:: https://travis-ci.org/cthoyt/onto2nx.svg?branch=master
    :target: https://travis-ci.org/cthoyt/onto2nx
    :alt: Build Status

.. |coverage| image:: https://codecov.io/gh/cthoyt/onto2nx/coverage.svg?branch=develop
    :target: https://codecov.io/gh/cthoyt/onto2nx?branch=develop
    :alt: Code coverage Status

.. |python_versions| image:: https://img.shields.io/pypi/pyversions/onto2nx.svg
    :alt: Supported Python Versions

.. |pypi_version| image:: https://img.shields.io/pypi/v/onto2nx.svg
    :alt: Current version on PyPI

.. |pypi_license| image:: https://img.shields.io/pypi/l/onto2nx.svg
    :alt: GPL 3.0 License

.. |zenodo| image:: https://zenodo.org/badge/DOI/10.5281/zenodo.1478027.svg
   :target: https://doi.org/10.5281/zenodo.1478027
