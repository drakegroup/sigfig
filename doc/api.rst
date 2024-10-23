API Documentation
#################

This guide explains the interface to the :meth:`round` function along with all the accepted parameters and how they effect the output:

----

Arguments
=========

The first argument specifies the number to be rounded and/or reformatted.  Can be of any numeric data type or type which can be interpreted as a number (ie. string '1.567').  The type of the returned value will be the same as this argument's type unless otherwise specified by the ``type`` keyword argument or by including uncertainty.  :exc:`ValueError` will be raised in the event of uninterpretable input.

The second argument specifies either the number of significant figures (if :class:`int` data type), or the uncertainty to which the first argument will be rounded (if any numeric-interpreted data type is given aside from :class:`int`).  :exc:`ValueError` will be raised in the event of uninterpretable input.

Additional arguments (aside from the keyword arguments specified below) are ignored

----

Rounding Operations
===================

Only 1 of the 3 rounding operation may be used at a time.  In the event multiple operations are requested, rounding by uncertainty will take precedence over rounding by significant figures which will take priority over rounding by number of decimals.  Selecting a rounding operation is not mandatory and can be ignored when :meth:`round` is being called strictly for formatting operations.

sigfigs
-------

Default value: ``None``

Controls how many significant figures the given number is to be rounded to in accordance with `significant figures rounding rules <https://en.wikipedia.org/wiki/Significant_figures#Significant_figures_rules_explained>`_.  Can be specified with ``sigfigs`` keyword argument or by passing as 2nd argument of type :class:`int`.  When specified, it should be an :class:`int` greater than 0.

.. code:: python

    >>> from sigfig import round
    >>> round(12.7654, sigfigs=4)
    12.77
    >>> round(12.7654, 3)
    12.8

decimals
--------

Default value: ``None``

Controls how many decimal places (or negative ten's power) the given number is to be rounded to in accordance with `decimal place rounding rules <https://en.wikipedia.org/wiki/Significant_figures#Rounding_and_decimal_places>`_.  When specified, it should be an :class:`int` of any value.

.. code:: python

    >>> from sigfig import round
    >>> round(12.7654, decimals=3)
    12.765
    >>> round('12.7654', decimals=-1)
    '10'

uncertainty
-----------

Default value: ``None``

Takes the uncertainty which will determine how many decimal places the given number is rounded to in accordance with :ref:`Uncertainty Rounding Rules` and ``cutoff`` value (default value: 9).  In the default ``cutoff`` case these rules dictate that the uncertainty is rounded to 1 significant figure and the given number is rounded to the same number of decimals as the uncertainty.
By specifying an uncertainty, both the rounded number and rounded uncertainty will be returned (in a string separated by " ± " by default)
Can be specified with ``uncertainty``/``unc`` keyword argument or by passing as 2nd argument in numeric-interpreted type (except :class:`int`) to :meth:`round`.

.. code:: python

    >>> from sigfig import round
    >>> round('3.14159', uncertainty='0.6567')
    '3.1 ± 0.7'
    >>> round(3.14159, 0.001567)
    '3.142 ± 0.002'

Uncertainty Rounding Rules
==========================

A number's uncertainty or error is a measure of how accurate that number is.  Consequently, the uncertainty's order of magnitude (aka number of decimals) is of greater importance than it's value resulting in the uncertainty usually being displayed with only 1 significant figure so as to not distract from it's associated number.  However, many of those in the scientific community will give 2 figures of uncertainty if the uncertainty begins with a 1 or 2.  One prominent research group (The Particle Data Group) rounds their measured uncertainties to 2 decimal places if they begin with 35 (after being rounded) and will round to 1 decimal place if they begin with 36 or higher.  This behavior is modified through the ``cutoff`` keyword argument which will always round to 1 decimal place in the event of ``cutoff=9``, round to 2 decimal places if the uncertainty begins with a 1 or 2 with ``cutoff=29`` (numbers beginning with 3-9 will be rounded to 1 decimal), and The Particle Data Group's preference sets ``cutoff=35``.

Following the rounding of the uncertainty, the given number (not uncertainty) will be rounded to the smallest magnitude of the resulting rounded uncertainty.  After all it would be confusing (or even misleading) to state a number with 6 decimals of accuracy when you're uncertain of any digit beyond the first decimal point.

cutoff (crop)
-------------

Default value: ``9``

The uncertainty magnitude value (:class:`int` ≥ 9) after which the uncertainty value is rounded with 1 less digit.

.. code:: python

    >>> from sigfig import round
    >>> round('3.14159', '0.6567', cutoff=65)
    '3.1 ± 0.7'
    >>> round('3.14159', '0.6567', cutoff=66)
    '3.14 ± 0.66'
    >>> round('3.14159', '0.6567', crop=77)
    '3.14 ± 0.66'

----

Formatting Output
=================

notation (form)
---------------

Default value: ``'standard'``

Output number format notation can be one of ``standard``/``std`` (default) for `standard notation` without exponentiation, ``engineering``/``eng`` for `engineering notation <https://en.wikipedia.org/wiki/Engineering_notation>`_, or ``scientific``/``sci`` for `scientific notation <https://en.wikipedia.org/wiki/Scientific_notation>`_.

.. code:: python

    >>> from sigfig import round
    >>> round('3679.14159', decimals=2, notation='scientific')
    '3.67914E3'
    >>> round('16248055.209', notation='eng')
    '16.248055209E6'
    >>> round('16248055.209', '19923.456', notation='eng')
    '16.25E6 ± 0.02E6'

.. note:: Should not be used in conjunction with kwarg ``format``/``style`` or ``type``/``output_type`` (since that would essentially be asking for conflicting outputs).

output_type (type)
------------------

Default value: ``type(arg[0])``

Return type can be any numeric-interpreted type (i.e. :class:`decimal.Decimal`, :class:`float`, :class:`str`, :class:`int`) and should not be a string of that type (i.e. Use ``float`` instead of ``'float'``).

.. code:: python

    >>> from sigfig import round
    >>> from decimal import Decimal
    >>> round('3679.14159', decimals=2, output_type=float)
    3679.14
    >>> round(16248055.209, type=Decimal)
    Decimal('16248055.209')

.. note:: Should not be used in conjunction with kwarg ``format``/``style`` or ``notation``/``form`` (since these will require :class:`str` output type).

spacing
-------

Default value: ``None``

Adds a ``spacer`` character every ``spacing``'th digit.  Should be :class:`int` ≥ 1.

.. code:: python

    >>> from sigfig import round
    >>> round('3679.14159', spacing=3, spacer=' ')
    3 679.141 59
    >>> round('94916248055.209', spacing=5, spacer=',')
    '9,49162,48055.209'

spacer
------

Default value: ``''``

Adds a ``spacer`` character (string) every ``spacing``'th digit.

decimal
-------

Default value: ``'.'``

Changes the decimal point character (:class:`str`).

.. code:: python

    >>> from sigfig import round
    >>> round('3679.14159', decimals=2, decimal=',')
    '3679,14'

Formatting Output with Uncertainty
==================================

separation (sep)
----------------

Default value: ``' ± '``

Changes the string which separates a number from it's uncertainty.  Recognizes the special strings ``'brackets'`` for in-line bracketed uncertainty, ``'external_brackets'`` for the special case of uncertainties greater than 10, and :class:`tuple` or :class:`list` which allows number and uncertainty to be stored independently.

.. code:: python

    >>> from sigfig import round
    >>> round('3679.14159', '0.00123', separation='+/-')
    '3679.142+/-0.001'
    >>> round('3679.14159', 0.000123, sep='brackets')
    '3679.1416(1)'
    >>> round('97.74159', 0.393, sep=tuple)
    ('97.7', '0.4')
    >>> round('3679990.14159', '123.00123', sep='brackets')
    '36800(1)00'
    >>> round('3679990.14159', '123.00123', sep='external_brackets')
    '3680000(100)'

format (style)
--------------

Default value: ``None``

Allows choice of predefined formats ``'Drake'`` and ``'PDG'`` for `The Drake Group's <http://drake.sharcnet.ca/>`_ preferred formatting of ``cutoff=29, spacer=3, spacing=' ', separation='brackets'`` and `The Particle Data Group's <http://pdg.lbl.gov/>`_ preferred formatting of ``cutoff=35`` (see `5.3 Rounding <http://pdg.lbl.gov/2011/reviews/rpp2011-rev-rpp-intro.pdf>`_).

.. code:: python

    >>> from sigfig import round
    >>> round('3679990.14159', '0.00125', format='Drake')
    '3 679 990.141 6(1 3)'
    >>> round('3679990.14159', '0.00125', style='PDG')
    '3679990.1416 ± 0.0013'

.. note:: Should not be used in conjunction with kwarg ``output_type``/``type`` or ``notation``/``form``.

----

Other "Features"
================

order of keyword arguments
--------------------------

The interface for :meth:`round` allows for conflicting keyword arguments (i.e. ``cutoff=19, cutoff=20`` or ``format='Drake', sep='+/-'``) where subsequent kwargs overwrite what comes before them.  However, this feature assumes insert-ordered :class:`dict`\ionaries which is not guaranteed until Python 3.7 (and beyond).  If you are using :mod:`sigfig` with earlier versions of Python (before 3.7) without insert-ordered :class:`dict`'s the recommended usage is to avoid conflicting keyword arguments.

prefix
------

Default value: ``None``

This is an experimental feature which adds a `metric SI unit prefix <https://en.wikipedia.org/wiki/Metric_prefix#List_of_SI_prefixes>`_ to the end of the outputted string (or multiple prefixes in the case of very big or very small numbers).  This feature behaves similar to engineering notation except using prefixes instead of exponents.  It has some unresolved edge cases that can be fully flushed out if found useful and requested.

.. code:: python

    >>> from sigfig import round
    >>> round('3679990.14159', '97654', style='Drake', prefix=True)
    '3.68(10)M'
    >>> round('3.67999014159E-10', '0.00125E-10', prefix=True)
    '(368.0 ± 0.1)p'

zero behavior
-------------

Any number with a value of zero that is known to 1 or more decimal places will be represented with all trailing zeros (ie. 0.00 is known to 2 decimal places and all trailing zeros are displayed).  Conversely any number with a value of zero that is known to -1 or fewer decimal places will be represented with only 1 digit (ie. 000 will only be displayed as 0).  The only exception is in the case of (non-external) bracketed uncertainty when the number is zero and known to -1 or fewer decimal places.  Below is an example of each scenario:

.. code:: python

    >>> from sigfig import round
    >>> round('0.00004567', decimals=3)
    '0.000'
    >>> round('23', '4732')
    '0 ± 5000'
    >>> round('23', '4732', sep='brackets')
    '0(5)000'

warning suppression
-------------------

While it's recommended to use Python's built-in warning control through `from warnings import filterwarnings` to define which warnings are presented, you can explicitly define warning behavior with this interface:

.. code:: python

    >>> from sigfig import round
    >>> round('12', sigfigs=5)
    sigfig.py:587: UserWarning: warning: 5 significant figures requested from number with only 2 significant figures
    '12.000'
    >>> round('12', sigfigs=4, warn=False)
    '12.00'
