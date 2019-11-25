Project Development & Roadmap
=============================

Initial Motivation
------------------

This project was created to add needed features to Python's built-in :func:`round` function.
Namely:

    - the ability to consistently round floating point numbers despite `float's inherent lack of precision <https://docs.python.org/3/tutorial/floatingpoint.html>`_.
    - the ability to round a number by number of significant figures/digits instead of by decimal places only.
    - the ability to round a number by its associated uncertainty.

Additional features were also needed to format numeric values for scientific publications.  Namely:

    - displaying a number with its associated uncertainty - in bracketed form - with a space between every thousand(th)s

----

Next Steps
----------

The Ultimate goal of the project is to add the included rounding features to the Python standard library.  This will require some refactoring among other tasks before the first pull request should be made.  This work is outlined in the following sections:

Separate out formatting code
############################

The code for formatting the resultant rounded number string does not belong in the standard library's :func:`round` function but would make more sense as either it's own package, as part of the :mod:`numpy <https://pypi.org/project/numpy/>` package, or as part of another package involving numeric or data visualization.
This will have the added benefit of making :mod:`sigfig`'s code more readable which is never a bad thing.

Increase numeric storage efficiency and standardization
#######################################################

:mod:`sigfig` currently parses numbers by first converting to string and then storing in a {<ten's power>:<numeric value>} dict (see :class:`_Number` in `source <github/sigfig/sigfig.py>`_ for technical details).  While this guarantees bug-free functionality for all numbers and is suitable for numbers already stored as strings, this lacks efficiency for :class:`decimal.Decimal` and :class:`float`.  Numeric values could possibly be stored instead using the same storage technique employed by the :class:`decimal.Decimal` package (after an investigation of that technique to ensure full code coverage).  This should fully satisfy the :class:`decimal.Decimal` case whereas the :class:`float` case can be handled as-is by default but allowed to optionally (with ``high_speed=True`` instead of the default ``high_accuracy=True``) use floating point arithmetic when speed trumps accuracy.

Interface Overhaul
##################

The current interface is multi-dimensional and very forgiving which allows for a wide range of allowable but unexpected behaviours instead of warning/crashing if a user strays from typical use cases.  While this suit's the project's current scrappy state, a redesign of the interface-handling :func:`_arguments_parse` function is recommended before merging with the standard library.

----

Possible Features
-----------------

Other features looking for implementation by any potential contributers are welcomed, would be greatly appreciated, are detailed below, and (subjectively) ordered by priority:

Baking and User-Defined Formats/Styles
######################################

The ability to "bake" default behaviour into :meth:`round` (essentially `partial application <https://en.wikipedia.org/wiki/Partial_application>`_, like you might do with :func:`functools.partial`) could allow for many desirable customizations.  Some examples are:

    - rounding by number of decimals instead of significant figures by default through something like ``round.bake(round_by_decimals=True)``  
    - always spacing numbers by 3 (in the case where output is of type :class:`str`) through ``round.bake(spacing=3, spacer=' ')``

Warnings, Alerts, and Feedback
##############################

Certain actions and usages of :meth:`round` warrant feedback given to the user.  These include (but are not limited to) the following:

    * warning for invalid keyword arguments
    * warning for depreciated usages
    * warning when out of range values are passed
    * informing when conflicting inputs are provided
    * informing when any data is passed implicitly instead of explicitly.  For example: ``round(3.2, 1)`` versus ``round(3.2, sigfigs=1)``

Units, Formatted Numbers, and Unit Prefixes
###########################################

Modification of the :meth:`_num_parse` function can be made without much effort to allow for formatted numbers (ie. ``'1,237.0'``), currency (ie. ``'$3,157.00'``), or numeric data with units (ie. ``'3475.2753nm'``) to be accepted.  This formatting data can be parsed and interpreted alongside the numeric data and the resulting output from the :meth:`round` operation can be given (by default) in the same format as the input was given.

Also, common units with their prefixes can be parsed so that more suitable prefixes for units can be chosen or explicitly specified by a new keyword argument.  For example:

    >>> round('3475.2753nm', '45.9479nm')
    '3.48 ± 0.05 μm'
    >>> round('3475.2753nm', '45.9479nm', units='cm', sep='brackets')
    '0.000348(5) cm'

Documentation: Figure(s) for Rounding Rules
###########################################

The :ref:`Uncertainty Rounding Rules` section may be confusing to those unfamiliar with the concept and would benefit from visual aid.  This can help to disambiguate like-sounding terms like "uncertainty", "magnitude of uncertainty", "number's uncertainty", and "error" as well as "number", "given number", and "number of decimals".

Input Precision
###############

Input precision is not currently stored.  In cases where a number is rounded to more decimals than it was given (ie. ``round(1.23, 0.000073)``) a warning can be thrown stating `"implicit uncertainty (0.005) greater than provided uncertainty (0.000073).  Provided uncertainty will be used."` since (in this case) the value 1.23 could be representing any value between 1.225 and 1.2349999….

Formatting of Exponentials
##########################

The exponentials resulting from scientific and engineering notation are separated from the number & uncertainty with an uppercase "E" present in both the number and resulting uncertainty.  Some might find it useful to customize the character(s) and/or optionally only appended the character after the uncertainty and not after the number.

Parse Number Last (small efficiency increased)
##############################################

A small gain to efficiency can be made by first parsing the uncertainty, number of decimals, or number of significant figures (aka the rounder) since these dictate how many digits are relevant in the given number.  With the rounder known, the parsing of the given number can be quicker since digits beyond what the rounder dictates can be discarded.  This will require a re-design of :meth:`_num_parse` where the exponential information is parsed first and will only be of (limited) benefit when the number is given with exponential notation (unless it's known to not have a trailing exponent).

----

Contributor Notes
-----------------

:mod:`sigfig` was developed with a few :pep:`20` idioms in mind:

    - Beautiful is better than ugly.
    - Explicit is better than implicit.
    - Simple is better than complex.
    - Complex is better than complicated.
    - Readability counts.

Refer to :pep:`8` and the `Google Python Style Guide <http://google.github.io/styleguide/pyguide.html>`_ for best practices when in doubt and thank you for considering contribution :)
