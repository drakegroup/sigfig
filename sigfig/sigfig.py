#!/usr/bin/python
# -*- coding: utf-8 -*-

from decimal import (Context, Decimal, InvalidOperation, Overflow, MAX_EMAX, MIN_EMIN,
                     ROUND_05UP, ROUND_CEILING, ROUND_DOWN, ROUND_FLOOR,
                     ROUND_HALF_DOWN, ROUND_HALF_EVEN, ROUND_HALF_UP, ROUND_UP)
from copy import copy
from html import escape
from re import fullmatch
from warnings import warn, filterwarnings, resetwarnings

import numbers

from inspect import currentframe, getfile
def _warn_stacklevel(best_guess=2):
    '''Helper function to associate warnings with caller outside this module.

    Args:
        best_guess: stack depth estimate in case the Python interpreter doesn't support stack introspection.
    Returns:
        integer stack level for warnings.warn() function.

    Note:
    - Python 3.12 should simplify this process with 'skip_file_prefixes' once the path normalization bugs are fixed.
    '''
    stacklevel = 0
    try:
        frame = currentframe()
        while True:
            if frame is None or getfile(frame) != __file__:
                return stacklevel
            frame = frame.f_back
            stacklevel += 1
    except:
        return best_guess

_manual_settings = {}
_default_settings = {
    'spacing': 0.1,
    'spacer': '',
    'decimal': '.',
    'separator': ' ± ',
    'cutoff': 9,
    'prefix': False,
    'exponent': 'E',
    'mode': ROUND_HALF_UP,
    'markup': None,
    'round_by_sigfigs': False,
    'round_by_decimals': True,
    'given_sigfigs': 0}
_major_prefixes = {
    24: ['Y', 'septillion'],
    21: ['Z', 'sextillion'],
    18: ['E', 'quintillion'],
    15: ['P', 'quadrillion'],
    12: ['T', 'trillion'],
    9: ['G', 'billion'],
    6: ['M', 'million'],
    3: ['k', 'thousand'],
    0: ['',''],
    -3: ['m', 'thousandth'],
    -6: ['μ', 'millionth'],
    -9: ['n', 'billionth'],
    -12: ['p', 'trillionth'],
    -15: ['f', 'quadrillionth'],
    -18: ['a', 'quintillionth'],
    -21: ['z', 'sextillionth'],
    -24: ['y', 'septillionth']}
_minor_prefixes = {
    2: ['h', 'hundred'],
    1: ['da', 'ten'],
    -1: ['d', 'tenth'],
    -2: ['c', 'hundredth']}

class _Number:
    '''
    Private data structure for storing & manipulating numbers

    Attributes:
        .value: Decimal holding the number and its significant trailing zeros
        ._exponent: lowest stored power of ten, without extracting Decimal digits
        ._zero_power: highest displayed power of ten for zero
    Attributes/Mehtods for inspection (getting values):
        .sign:     string of either '+' or '-', denoting sign of stored number
        .nan:      bool True/False depending on whether number is NaN
        .positive: bool True/False depending on number's sign
        .negative: bool True/False depending on number's sign
        .has_uncertainty: bool True/False depending on whether there is an associated uncertainty with this number
        .max_power(): returns integer corresponding to number's highest populated 10's power
        .min_power(): returns integer corresponding to number's lowest populated 10's power
        .decimate(dict, _Number, bool, bool): returns string of all digits in given format
            specifying spacing and non-standard decimal point, optional sign
            optionally embedded uncertainty, and optional leading/trailing zeros
        .output(type): returns number in given type
    Methods for manipulation (changing the value):
        .set_sign(str): function used to change/set the number's sign by passing '-' or '+'
                        so that .positive, .negative, .sign don't need manual updating
        .increment_power_by(int): shifts the Decimal exponent by the given value
        .round_by_decimals(int):  performs rounding operation to the given 10's power
        .prefixify(str):          converts to Scientific or Engineering notation with optional SI prefix
    '''
    def __init__(self, value=Decimal(0), exponent=0):
        self.value = value
        self._exponent = exponent
        self._zero_power = 0
        self.prefix = ''
        self.has_uncertainty = False
    @property
    def negative(self):
        return self.value.is_signed()
    @property
    def positive(self):
        return not self.negative
    @property
    def sign(self):
        return '-' if self.negative else '+'
    @property
    def zero(self):
        return self.value.is_zero()
    @property
    def nan(self):
        return self.value.is_nan()
    @property
    def sigfigs(self):
        return self.max_power() - self.min_power() + 1
    def set_sign(self, sign='+'):
        '''sets the number's sign'''
        if sign not in ('+', '-'):
            warn('sign must be "+" or "-", assuming positive', stacklevel=_warn_stacklevel(4))
            sign = '+'
        self.value = self.value.copy_abs()
        if sign == '-':
            self.value = self.value.copy_negate()
    def max_power(self):
        '''returns integer corresponding to number's highest populated 10's power'''
        return self._zero_power if self.zero else self.value.adjusted()
    def min_power(self):
        '''returns integer corresponding to number's lowest populated 10's power'''
        return self._exponent
    @staticmethod
    def _context(precision):
        return Context(prec=max(1, precision), rounding=ROUND_HALF_UP,
                       Emin=MIN_EMIN, Emax=MAX_EMAX, clamp=0,
                       traps=[InvalidOperation, Overflow])
    def increment_power_by(self, power):
        '''shifts the number by an exact power of ten'''
        self.value = self.value.scaleb(power, context=self._context(self.sigfigs))
        self._exponent += power
        self._zero_power += power
    def round_by_decimals(self, decimals, mode=ROUND_HALF_UP):
        '''performs rounding operation to the given 10's power'''
        last_power = -int(decimals)
        highest_power = self.max_power()
        self.value = self.value.quantize(Decimal((0, (1,), last_power)),
                                         rounding=mode,
                                         context=self._context(highest_power - last_power + 2))
        self._exponent = last_power
        if self.zero:
            self._zero_power = max(highest_power, last_power)
            if last_power > highest_power:
                self.set_sign('+')
    def decimate(self, format, unc=None, zeropadding=True, sign=True, units=''):
        '''
        returns string of all digits in given format {spacing, left_spacer, right_spacer, decimal},
        with unc=_Number for embedded uncertainty, and optional leading/trailing zeros & sign
        '''
        highest_power = self.max_power()
        lowest_power = self.min_power()
        digits = self.value.as_tuple().digits
        top = highest_power
        bot = lowest_power
        if zeropadding:
            top = max(top, 0)
            bot = min(bot, 0)
        if self.zero and not unc and top > 0:
            top = 0
        output = []
        if sign and self.negative:
            output.append('-')
        for power in range(top, bot - 1, -1):
            index = highest_power - power
            output.append(str(digits[index]) if 0 <= index < len(digits) else '0')
            if power == lowest_power and unc:
                output.append('('+unc.decimate(format, zeropadding=False, sign=False)+')')
            if power != bot:
                if power == 0:
                    output.append(format['decimal'])
                elif power % format['spacing'] == 0:
                    output.append(format['left_spacer' if power > 0 else 'right_spacer'])
        return ''.join(output) + units
    def output(self, output_type):
        '''returns number in given type'''
        if output_type in (Decimal, int, float):
            return output_type(self.value)
        if issubclass(output_type, numbers.Integral):
            return output_type(int(self.value))
        return output_type(str(self.value))
    def __gt__(self, other):
        return self.value.copy_abs() > other.value.copy_abs()
    def prefixify(self, prefix, exponent):
        '''converts to Engineering/Scientific notation with optional SI prefix'''
        #self.prefix = 'XXX'
        #return None
        self.prefix = ''
        power_shift = 0
        if prefix == 'sci':
            p = self.max_power()
            self.prefix = exponent + str(p)
            self.increment_power_by(-p)
            power_shift += -p
            return power_shift
        elif prefix == 'eng':
            p0 = 0
            if self.max_power() < 0:
                p0 = 2
            p = int((self.max_power() - p0)/3)*3
            self.prefix = exponent + str(p)
            self.increment_power_by(-p)
            power_shift += -p
            return power_shift
        elif prefix in ['all', 'minor']:
            prefixes = {**_major_prefixes, **_minor_prefixes}
            p = self.min_power()
            while p >= min(prefixes):
                if p in prefixes:
                    break
                p -= 1
        else:
            #prefix in [True, 'major', 'eng']:
            prefixes = _major_prefixes
            #p = int((self.min_power()-1)/3)*3
            p = self.max_power()
            while p > max(prefixes)+3:
                self.prefix += prefixes[max(prefixes)][0]
                self.increment_power_by(-max(prefixes))
                power_shift += -max(prefixes)
                p -= max(prefixes)
            while p < min(prefixes):
                self.prefix += prefixes[min(prefixes)][0]
                self.increment_power_by(-min(prefixes))
                power_shift += -min(prefixes)
                p -= min(prefixes)
            p0 = 0
            if self.max_power() < 0:
                p0 = 2
            p = int((self.max_power() - p0)/3)*3
        self.prefix = prefixes[p][0] + self.prefix
        self.increment_power_by(-p)
        power_shift += -p
        return power_shift

def _arguments_parse(args, kwargs):
    '''Private function for use only in round() function:
    Deciphers user intent based on given inputs along with preset defaults
    which returns actionable and summarized useful variables in a dict.
    '''
    given = {'reset_warnings': False}

    if any([w in kwargs for w in ('warn', 'warning', 'warnings')]):
        warning = kwargs.get('warn') or kwargs.get('warning') or kwargs.get('warnings')
        if not warning:
            filterwarnings('ignore')
        elif warning == True:
            resetwarnings()
        else:
            resetwarnings()
            warn(f'warnings argument expected to be True, False, or "once". Got "{warning}"', stacklevel=_warn_stacklevel(3))
        given['reset_warnings'] = True

    types = (numbers.Number, str, Decimal, _Number, type(None))
    given['output_type'] = type(args[0])
    if not isinstance(args[0], types):
        raise TypeError(f'Invalid input type of {type(args[0])}, expecting 1 of {types}')
    given['num'] = _num_parse(args[0])
    if len(args) >= 2:
        if type(args[1]) == int:
            given['sigfigs'] = args[1]
            if given['sigfigs'] < 1:
                warn('cannot have less that 1 significant figure, setting to 1', stacklevel=_warn_stacklevel(3))
                given['sigfigs'] = 1
        elif args[1] != args[1]:
            warn(f'Ignoring 2nd argument "{args[1]}". invalid uncertainty, expecting number', stacklevel=_warn_stacklevel(3))
        else:
            given['uncertainty'] = _num_parse(args[1])
            given['output_type'] = str
    if len(args) > 2:
        warn(f"last {int(len(args) - 3)} argument(s) discarded/ignored", stacklevel=_warn_stacklevel(3))
    
    for key in _manual_settings:
        given[key] = _manual_settings[key]

    keys = {'separator', 'separation', 'sep', 'format', 'sigfigs', 's', 'decimals', 'd', 'uncertainty', 'u', 'cutoff', 'spacing', 'spacer', 'left_spacer', 'right_spacer', 'decimal', 'output_type', 'output', 'type', 'style', 'prefix', 'exponent', 'notation', 'form', 'crop', 'markup', 'render', 'mode'}
    for key in kwargs:
        val = kwargs[key]
        if key not in keys:
            warn(f'unrecognized argument, skipping {key}={val}', stacklevel=_warn_stacklevel(3))
            continue
        if key in given and key not in _manual_settings:
            None
            #warn("overwriting %s=%s with %s=%s" % (key, given[key], key, val))
        if key in {'sigfigs', 's', 'decimals', 'd', 'cutoff', 'crop'}:
            shortcuts = {'s':'sigfigs', 'd':'decimals'}
            key = shortcuts[key] if key in shortcuts else key
            try:
                if key == 'crop':
                    key = 'cutoff'
                if not isinstance(val, numbers.Integral):
                    warn(f'use integer type for {key} argument', stacklevel=_warn_stacklevel(3))
                if key in {'cutoff', 'crop'} and int(val) < 9:
                    warn('cutoff/crop cannot be < 9, setting to 9', stacklevel=_warn_stacklevel(3))
                    val = 9
                if key == 'sigfigs' and int(val) < 1:
                    warn('cannot have less that 1 significant figure, setting to 1', stacklevel=_warn_stacklevel(3))
                    val = 1
                given[key] = int(val)
            except:
                warn(f'Ignoring {key}={val}, invalid type of {type(val)}, expecting integer type', stacklevel=_warn_stacklevel(3))
        elif key in {'uncertainty', 'u'}:
            try:
                assert(val == val)
                given['uncertainty'] = _num_parse(val)
                given['output_type'] = str
            except:
                warn(f"Ignoring {key}={val}. invalid uncertainty, expecting number", stacklevel=_warn_stacklevel(3))
        elif key == 'mode':
            if val in (ROUND_05UP, ROUND_CEILING, ROUND_DOWN, ROUND_FLOOR,
                       ROUND_HALF_DOWN, ROUND_HALF_EVEN, ROUND_HALF_UP, ROUND_UP):
                given[key] = val
            else:
                warn(f"Ignoring {key}={val}, invalid rounding mode", stacklevel=_warn_stacklevel(3))
        elif key == 'prefix':
            if type(val) == bool or val in {'major', 'sci', 'eng'}:
                given[key] = val
            elif val in ['minor', 'all']:
                given['prefix'] = 'all'
            else:
                prefixes = { True, False, 'major', 'minor', 'sci', 'eng', 'all'}
                warn(f"Ignoring {key}={val}, invalid prefix setting, expecting 1 of: {prefixes}", stacklevel=_warn_stacklevel(3))
                continue
            given['output_type'] = str
        elif key in {'spacer', 'left_spacer', 'right_spacer', 'decimal'}:
            given[key] = str(val)
            if key == 'spacer':
                given['left_spacer'] = given['right_spacer'] = str(val)
            given['output_type'] = str
        elif key == 'spacing':
            given['spacing'] = int(val)
            given['output_type'] = str
        elif key in {'markup', 'render'}:
            markups = {'latex': 'tex', 'tex': 'tex', 'markdown': 'html',
                       'md': 'html', 'html': 'html', 'rst': 'rst'}
            if val is None:
                given['markup'] = None
            elif isinstance(val, str) and val.lower() in markups:
                given['markup'] = markups[val.lower()]
            else:
                warn(f'Ignoring {key}={val}, expecting LaTeX/tex, markdown/md, rst, or HTML', stacklevel=_warn_stacklevel(3))
        elif key in {'sep', 'separation', 'separator'}:
            if val == 'external_brackets':
                given['separator'] = 'brackets'
                given['external_brackets'] = True
                continue
            elif val == 'brackets':
                given['separator'] = 'brackets'
            elif val in {tuple, list}:
                given['output'] = val
                given['output_type'] = type(args[0])
            elif val == 'tuple':
                given['output'] = tuple
                given['output_type'] = type(args[0])
            elif val == 'list':
                given['output'] = list
                given['output_type'] = type(args[0])
            given['separator'] = str(val)
        elif key in ['format', 'style', 'output', 'type', 'output_type', 'notation', 'form']:
            given['output_type'] = str
            #warning might be warranted if output_type previously specified
            properties = ['spacing', 'spacer', 'decimal', 'separator', 'cutoff', 'prefix', 'form']
            formats = {'English': [3, ',', '.', ' ± ', 9, False,  '#,###,###.## ± 0.#'],
                       'French':  [3, ' ', ',', ' ± ', 99, False, '# ### ###,## ± 0,##'],
                       'other':   [3, '.', ',', ' ± ', 99, False, '#.###.###,## ± 0,##'],
                       'PDG':     [.1, '', '.', ' ± ', 35, False,  '# ### ###.##(##)'],
                       'Drake':   [3, ' ', '.', 'brackets', 29, False, '# ### ###.##(##)'],
                       'sci':     [.1, '', '.', ' ± ', 9, 'sci', '# ### ###.##(##)'],
                       'eng':     [.1, '', '.', ' ± ', 9, 'eng', '# ### ###.##(##)'],
                       'std':     [.1, '', '.', ' ± ', 9, False, '# ### ###.##(##)']}
            outputs = {'+-', 'map'}
            notations = {'sci', 'scientific', 'eng', 'engineering', 'std', 'standard'}
            if val in notations:
                val = val[:3]
                if val == 'sta':
                    val = 'std'
                for i, prop in enumerate(properties):
                    #if prop in given and key not in _manual_settings:
                    if prop in given:
                        continue
                        #warn("overwriting %s=%s with %s=%s" % (prop, given[prop], prop, formats[val][i]))
                    given[prop] = formats[val][i]
            elif val in formats:
                for i, prop in enumerate(properties):
                    if prop in given and key not in _manual_settings:
                        None
                        #warn("overwriting %s=%s with %s=%s" % (prop, given[prop], prop, formats[val][i]))
                    given[prop] = formats[val][i]
                    if prop == 'spacer':
                        given['left_spacer'] = given['right_spacer'] = given[prop]
            elif isinstance(val, type) and issubclass(val, types):
                given['output_type'] = val
                if 'prefix' in given:
                    del given['prefix']
            elif val in outputs:
                if val == '+-':
                    given['separator'] = ' ± '
                else:
                    given['output'] = val
            else:
                warn(f"expected format of {[f for f in formats] + [o for o in outputs]}, ignoring format of {val}", stacklevel=_warn_stacklevel(3))
                given['output_type'] = type(args[0])
        else:
            given[key] = val

    if 'sigfigs' in given and 'decimals' in given:
        warn('Cannot round by both sigfigs & decimals, ignoring decimal constraint', stacklevel=_warn_stacklevel(3))
        del given['decimals']
    if 'uncertainty' in given and any([x in given for x in ['sigfigs', 'decimals', 'arg2']]):
        warn(
            'Cannot round by both uncertainty & decimals/sigfigs simultaneously, ignoring decimals &/or sigfigs.  Use seperate calls to round() function for seperate roundings.',
            stacklevel=_warn_stacklevel(3)
        )
        for prop in ['sigfigs', 'decimals', 'arg2']:
            if prop in given:
                del given[prop]
    if 'arg2' in given:
        if 'sigfigs' in given or 'decimals' in given:
            warn('Invalid 2nd argument, ignoring. "sigfigs" or "decimals" given in keyword arguments', stacklevel=_warn_stacklevel(3))
        elif _default_settings['round_by_sigfigs']:
            given['sigfigs'] = given['arg2']
        else:
            given['decimals'] = given['arg2']
        del given['arg2']
    if given.get('markup') is not None:
        given['output_type'] = str
    if not issubclass(given['output_type'], (numbers.Real, Decimal, _Number)):
        given['format'] = {}
        spacers = {'spacer', 'left_spacer', 'right_spacer'}
        if spacers.intersection(given) and 'spacing' not in given:
            given['spacing'] = 3
        if 'spacing' in given and not spacers.intersection(given):
            given['spacer'] = ","
        for prop in ('left_spacer', 'right_spacer'):
            given.setdefault(prop, given.get('spacer', _default_settings['spacer']))
        for prop in {'decimal', 'spacer', 'left_spacer', 'right_spacer', 'spacing'}:
            if prop in given:
                val = given[prop]
                del given[prop]
            elif prop in _manual_settings:
                val = _manual_settings[prop]
            else:
                val = _default_settings[prop]
            given['format'][prop] = val
    for prop in ['separator', 'prefix', 'exponent', 'markup', 'mode']:
        if prop in given:
            continue
        elif prop in _manual_settings:
            given[prop] = _manual_settings[prop]
        else:
            given[prop] = _default_settings[prop]

    return given
def _num_parse(num):
    '''Parses decimal text and legacy exponent markers into a Decimal-backed _Number.'''
    if isinstance(num, _Number):
        return copy(num)
    if num is None:
        warn('no number provided, assuming zero (0)', stacklevel=_warn_stacklevel(4))
        return _Number()
    if num != num:
        warn('given input is not a number (NaN)')
        number = _Number(num if isinstance(num, Decimal) else Decimal('NaN'))
        number._nan_input = num
        return number
    text = str(num)
    if text in ('', '.', '+', '-'):
        warn('no number provided, assuming zero (0)', stacklevel=_warn_stacklevel(4))
        return _Number()
    match = fullmatch(r'([+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+))?(?:[EeDdQq]([+-]?[0-9]*))?', text)
    if match is None:
        raise ValueError(f'parsing failed: invalid number {text!r}')
    coefficient, exponent = match.groups()
    if coefficient is None:
        warn('no number provided, assuming zero (0)', stacklevel=_warn_stacklevel(4))
        coefficient = '0'
    if exponent in ('', '+', '-'):
        warn('exponent expected but not provided', stacklevel=_warn_stacklevel(4))
        exponent = '0'
    power = int(exponent or '0')
    value = num if isinstance(num, Decimal) else Decimal(coefficient + 'E' + str(power))
    if value.is_zero():
        return _Number(Decimal(0).copy_sign(value))
    return _Number(value, power - len(coefficient.partition('.')[2]))

def round(*args, **kwargs):
    '''
    round a given number to either
        - a given number of significant figures/significant digits,
        - a given number of decimals, or
        - a given uncertainty
    and optionally output the number with given formatting along with its uncertainty

    Key usage examples:
        round('2.675', sigfigs=2) => '2.7'
        round(2.675, decimals=2)  =>  2.68
        round(199, sigfigs=1, mode=ROUND_DOWN) => 100
        round('2.675', '0.00197') => '2.675 ± 0.002'
        round('123456.789099', '-1.15E-4', output='Drake') => '123 456.789 10(12)

    For detailed usage instructions see https://pypi.org/project/sigfig/
    '''
    if not args:
        warn("no input number given, nothing to return", stacklevel=_warn_stacklevel(2))
        return None
    given = _arguments_parse(args, kwargs)
    num = given['num']
    mode = given['mode']

    if num.nan:
        return getattr(num, '_nan_input', num.value)
    if 'decimals' in given:
        num.round_by_decimals(given['decimals'], mode)
    elif 'sigfigs' in given:
        if given['sigfigs'] > num.sigfigs:
            warn(
                f"{given['sigfigs']} significant figures requested from number with only {num.sigfigs} significant figures",
                stacklevel=_warn_stacklevel(2)
            )
        last_power = num.max_power() - given['sigfigs'] + 1
        num.round_by_decimals(-last_power, mode)
        if num.sigfigs > given['sigfigs']:
            num.round_by_decimals(given['sigfigs'] - num.max_power() - 1, mode)
    elif 'uncertainty' in given:
        num.has_uncertainty = True
        if 'cutoff' in given:
            cutoff = str(given['cutoff'])
        elif 'cutoff' in _manual_settings:
            cutoff = str(_manual_settings['cutoff'])
        else:
            cutoff = str(_default_settings['cutoff'])
        unc = round(given['uncertainty'], sigfigs=len(cutoff), output='map', mode=mode)
        cut = _num_parse(cutoff + 'E' + str(unc.min_power()))
        if unc > cut:
            unc = round(given['uncertainty'], sigfigs=len(cutoff)-1, output='map', mode=mode)
            if not unc.zero and unc.value.copy_abs() < Decimal((0, (2,), unc.max_power())):
                unc.round_by_decimals(1 - unc.max_power(), mode)
        num.round_by_decimals(-unc.min_power(), mode)

    if given['prefix']:
        power_shift = num.prefixify(given['prefix'], given['exponent'])
        if 'uncertainty' in given:
            unc.increment_power_by(power_shift)
        if given['prefix'] in {'sci', 'eng'}:
            exponents = {'tex': r' \times 10^{{{power}}}',
                         'html': '×10<sup>{power}</sup>',
                         'rst': r' × 10\ :sup:`{power}`'}
            if given['markup'] in exponents:
                num.prefix = exponents[given['markup']].format(power=-power_shift)

    if given['reset_warnings']:
        resetwarnings()

    if issubclass(given['output_type'], (numbers.Number, Decimal)):
        if 'output' in given and given['output'] in {tuple, list}:
            if 'uncertainty' not in given:
                return given['output']([num.output(given['output_type'])])
            return given['output']([num.output(given['output_type']),
                                    unc.output(given['output_type'])])
        return num.output(given['output_type'])
    elif 'output' in given and given['output'] == 'map':
        return num

    if given['markup'] == 'html':
        for prop in ('decimal', 'left_spacer', 'right_spacer'):
            given['format'][prop] = escape(given['format'][prop])
        given['separator'] = escape(given['separator'])
    elif given['markup'] == 'tex':
        given['separator'] = given['separator'].replace('±', r'\pm')
    
    units = num.prefix if given['prefix'] else ''
    if 'uncertainty' in given and given['separator'] == 'brackets' and unc.min_power() > 0 and 'external_brackets' not in given:
        return num.decimate(given['format'], unc=unc, units=units)

    output = num.decimate(given['format'])

    if 'output' in given and given['output'] in {list, tuple}:
        if 'uncertainty' in given:
            return given['output']([output + units, unc.decimate(given['format'], sign=False, units=units)])
        return given['output']([output + units])

    if 'uncertainty' in given:
        if given['separator'] == 'brackets' and unc.min_power() > 0:
            output += '('+unc.decimate(given['format'], sign=False)+')'
        elif given['separator'] == 'brackets':
            output += '('+unc.decimate(given['format'], zeropadding=False, sign=False)+')'
        else:
            if given['prefix'] and given['prefix'] not in {True, 'major', 'minor', 'all'}:
                output += num.prefix
            output += given['separator'] + unc.decimate(given['format'], sign=False)
            if given['prefix'] == True and units:
                output = f'({output})'
    return output + units

def roundit(*args, **kwargs):
    '''Depreciated version of round() function with limited scope'''
    warn('Depreciated Usage: Migrate code to use round() function instead', DeprecationWarning, stacklevel=_warn_stacklevel(2))
    defaults = {'spacer': ' ', 'spacing': 3, 'separator': 'brackets', 'output_type' : str}
    final_parameters = defaults
    if 'form' in kwargs:
        if kwargs['form'] == 'plusminus':
            kwargs['separator'] = ' +/- '
        else:
            kwargs['separator'] = kwargs['form']
        del kwargs['form']
    if 'crop' in kwargs:
        kwargs['crop'] -= 1
    for key in kwargs:
        final_parameters[key] = kwargs[key]
    return round(*args, **final_parameters)
def round_unc(*args, **kwargs):
    '''Depreciated version of round() function with limited scope'''
    warn('Depreciated Usage: Migrate code to use round() function instead', DeprecationWarning, stacklevel=_warn_stacklevel(2))
    defaults = {'sep': tuple}
    final_parameters = defaults
    if 'form' in kwargs and kwargs['form'] == 'plusminus':
        kwargs['separator'] = ' +/- '
        del kwargs['form']
    if 'crop' in kwargs:
        kwargs['crop'] -= 1
    for key in kwargs:
        final_parameters[key] = kwargs[key]
    return round(*[str(arg) for arg in args], **final_parameters)[0]
def round_sf(number, sigfigs):
    '''Depreciated version of round() function with limited scope'''
    warn('Depreciated Usage: Migrate code to use round() function instead', DeprecationWarning, stacklevel=_warn_stacklevel(2))
    return round(str(number),sigfigs=sigfigs)
