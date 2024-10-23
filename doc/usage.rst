Usage Guide
===========

This page contains the most common use cases for the :mod:`sigfig` module.

First make sure that :mod:`sigfig` is :doc:`installed <install>`.

Quickstart
----------

Using the :mod:`sigfig` module's :meth:`round` function is very simple.

Begin by importing the module and adding its features to the built-in round function:

.. code:: python

    >>> from sigfig import round

let's round a number to 4 significant figures

.. code:: python

    >>> round(123.456, 4)
    123.5

but let's get in the habit of storing our numbers as :class:`str`\ings to circumvent :class:`float`'s `inherent lack of precision <https://docs.python.org/3/tutorial/floatingpoint.html>`_.
:meth:`round` will always return the rounded number in the same type it was given unless told otherwise:

.. code:: python

    >>> round('123.456', 4)
    '123.5'
    >>> from decimal import Decimal
    >>> round(Decimal(123456E-3), 3)
    Decimal('123')
    >>> round('123.456', 5, type=float)
    123.46

We can round numbers by number of decimals, by significant figures/digits, or by the number's :ref:`uncertainty <Uncertainty Rounding Rules>`:

.. code:: python

    >>> round('3.14159', sigfigs=2)
    '3.1'
    >>> round('3.14159', decimals=2)
    '3.14'
    >>> round('3.14159', uncertainty=2)
    '3 ± 2'

which the function will choose based on the type/context of the 2nd argument:

.. code:: python

    >>> round('3.14159', 2)
    '3.1'
    >>> round('3.14159', '0.0007524')
    '3.1416 ± 0.0008'

When rounding by uncertainties we can isolate the rounded number and/or uncertainty by setting the ``sep``\aration keyword argument to :class:`list` or :class:`tuple` :

.. code:: python

    >>> round('123456E-5', '123E-6', sep=tuple)[0]
    '1.2346'
    >>> round(123456E-5, 123E-6, sep=list, type=Decimal)
    [Decimal('1.2346'), Decimal('0.0001')]

Formatting
##########

We can use :meth:`round` to output numbers in a myriad of :ref:`different formats <Formatting Output>`:

.. code:: python

    >>> round('86375.25799', decimals=2, notation='sci') # scientific notation
    '8.637526E4'
    >>> round('86375.25799', sigfigs=3, notation='eng') # engineering notation
    '86.4E3'
    >>> round('86375.25799', '0.023759', format='PDG') # Particle Data Group preferred formatting
    '86375.258 ± 0.024'
    >>> round('863192837.1176159248', '.00002742764', format='Drake') # Drake Group preferred formatting
    '863 192 837.117 616(27)'

or we can create our own custom format either from scratch

.. code:: python

    >>> round('17265098762.12345678', .000000289, spacing=5, spacer=',', decimal='_', separation=' +/- ')
    '1,72650,98762_12345,68 +/- 0_00000,03'

or by modifying an existing format:

.. code:: python

    >>> round('86375.25799', '0.023759', format='PDG', sep='brackets')
    '86375.258(24)'
    >>> round('863192837.1176159248', '.00002742764', format='Drake', cutoff=22)
    '863 192 837.117 62(3)'

See the :doc:`api` for a more detailed explanation of all above-used features.
