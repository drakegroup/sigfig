sigfig
=======

.. image:: https://img.shields.io/pypi/v/sigfig.svg
    :target: https://pypi.org/project/sigfig/
    :alt: Version
.. image:: https://readthedocs.org/projects/sigfig/badge/?version=latest
    :target: http://sigfig.readthedocs.io/
    :alt: Documentation
.. image:: https://img.shields.io/pypi/pyversions/sigfig.svg
    :target: https://pypi.python.org/pypi/sigfig/
    :alt: Python Versions
.. image:: https://raw.githubusercontent.com/drakegroup/sigfig/refs/heads/master/test/coverage.svg
    :target: https://github.com/drakegroup/sigfig/actions/workflows/smoke_test.yaml
    :alt: Coverage Status

This is the **sigfig** Python package used for rounding numbers (with expected results).

.. code:: python

    >>> round(0.25, 1)
    0.2
    >>> from sigfig import round
    >>> round(0.25, decimals=1)
    0.3
    >>> round(3.14159, sigfigs=2)
    3.1
    >>> round(3.14159, uncertainty=0.003639)
    '3.142 ± 0.004'
    >>> round('3.141592653589793', '0.00000002567', format='Drake')
    '3.141 592 654(26)'

Key Features:

* round numbers by significant figures/digits
* round numbers by decimal places
* round numbers by uncertainty/error
* format numbers in a variety of common styles & notations
* read in numbers of any type

In-depth documentation can be found here:

* `Installation <https://sigfig.readthedocs.io/en/latest/install.html>`_
* `Usage Guide <https://sigfig.readthedocs.io/en/latest/usage.html>`_
* `API Documentation <https://sigfig.readthedocs.io/en/latest/api.html>`_
* `Project Development & Roadmap <https://sigfig.readthedocs.io/en/latest/roadmap.html>`_

Useful links:

.. |pypi| image:: https://raw.githubusercontent.com/drakegroup/sigfig/refs/heads/master/doc/pypi-logo.svg
    :target: https://pypi.org/project/sigfig
    :height: 1em
.. |github| image:: https://raw.githubusercontent.com/FortAwesome/Font-Awesome/refs/heads/master/svgs/brands/github.svg
    :target: https://github.com/drakegroup/sigfig
    :height: 1em

*  |pypi| `Python Package Index entry <https://pypi.org/project/sigfig>`_ 
*  |github| `Source Code <https://github.com/drakegroup/sigfig>`_

Please direct any comments/suggestions/feedback/bugs to `the issues page <https://github.com/drakegroup/sigfig/issues>`_ or `submit a pull request <https://sigfig.readthedocs.io/en/latest/roadmap.html#contribution-guide>`

Thanks for downloading :)
