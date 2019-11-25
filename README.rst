sigfig
======

.. image:: https://img.shields.io/pypi/v/sigfig.svg
    :target: https://pypi.org/project/sigfig/
    :alt: Version
.. image:: https://readthedocs.org/projects/sigfigs/badge/?version=latest
    :target: http://sigfigs-python-package.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation
.. image:: https://img.shields.io/pypi/pyversions/sigfig.svg
    :target: https://pypi.python.org/pypi/sh
    :alt: Python Versions
.. image:: https://codecov.io/gh/mikebusuttil/sigfig/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/mikebusuttil/sigfig/
    :alt: Coverage Status

This is the :mod:`sigfig` Python package used to manipulate and format numerical data for presentation.

    >>> round(0.25, 1)
    0.2
    >>> from sigfig import round
    >>> round(0.25, decimals=1)
    0.3
    >>> round(3.14159, 2)
    3.1
    >>> round(3.14159, 0.001567)
    '3.142 ± 0.002'
    >>> round(3.141592653589793, 0.00000002567, format='Drake')
    '3.141 592 654(26)'

In-depth documentation can be found here:

   install
   usage
   api
   roadmap

Useful links:

* Python Package Index entry: https://pypi.org/project/sigfig/
* Source Code: https://github.com/mikebusuttil/sigfig/

Please direct any comments/suggestions/feedback/bugs to mike.busuttil@gmail.com and valdezt@gmail.com

Thanks for downloading :)