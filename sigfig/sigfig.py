#!/usr/bin/python
# -*- coding: utf-8 -*-

from decimal import Decimal
from copy import deepcopy
from sortedcontainers import SortedDict
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
        .map: - dict for number storage
              - maps 10's power (key) to numeric value (value)
              - i.e. 3.14 => .map = {0:3, -1: 1, -2: 4}
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
        .increment_power_by(int): (de)increments all keys in .map by given value
        .round_by_decimals(int):  performs rounding operation to the given 10's power
        .prefixify(str):          converts to Scientific or Engineering notation with optional SI prefix
    '''
    def __init__(self):
        self.set_sign('+')
        self.prefix = ''
        self.has_uncertainty = False
        self.map = SortedDict()
        self.zero = False
        self.nan = False
    def set_sign(self, sign='+'):
        '''sets the number's sign'''
        if sign == '+':
            self.negative = False
            self.positive = True
            self.sign = '+'
        elif sign == '-':
            self.negative = True
            self.positive = False
            self.sign = '-'
        else:
            warn('sign must be "+" or "-", assuming positive', stacklevel=_warn_stacklevel(4))
            self.negative = False
            self.positive = True
            self.set_sign('+')
    def max_power(self):
        '''returns integer corresponding to number's highest populated 10's power'''
        return max(self.map)
    def min_power(self):
        '''returns integer corresponding to number's lowest populated 10's power'''
        return min(self.map)
    def increment_power_by(self, n):
        '''(de)increments all keys in .map'''
        tmp = SortedDict()
        for key in self.map:
            tmp[key + n] = self.map[key]
        self.map = tmp
    def round_by_decimals(self, decimals):
        '''performs rounding operation to the given 10's power'''
        last_power = -decimals
        tmp_map = SortedDict({self.max_power(): 0})
        tmp_map = SortedDict({last_power: 0})
        last_tmp_power = self.max_power()
        for key in range(self.max_power(), min(-decimals - 1, -1), -1):
            if key < last_power and key >= 0 or key not in self.map:
                float(0)
            #if key < last_power and key < 0:
            #    Decimal(3)
            #    continue
            else:
                last_tmp_power = key
                tmp_map[key] = self.map[key]
        if last_power == self.max_power() + 1:
            if self.map[self.max_power()] >= 5:
                tmp_map[last_power] = 1
            else:
                self.zero = True
                tmp_map = SortedDict({last_power:0})
                self.set_sign('+')
        elif last_power > self.max_power():
            self.zero = True
            tmp_map = SortedDict({last_power:0})
            self.set_sign('+')
        elif last_tmp_power - 1 in self.map and self.map[last_tmp_power - 1] >= 5:
            tmp_map[last_tmp_power] += 1
            tmp_power = last_tmp_power
            while tmp_map[tmp_power] == 10:
                tmp_map[tmp_power] = 0
                tmp_power += 1
                if tmp_power not in tmp_map:
                    tmp_map[tmp_power] = 1
                else:
                    tmp_map[tmp_power] += 1
        self.map = tmp_map
        '''if self.map == SortedDict({0:0}):
            self.zero = True
            self.set_sign('+')
            if self.has_uncertainty:
                if last_power < 0:
                    for p in range(-1, last_power - 1, -1):
                        self.map[p] = 0
                elif last_power > 0:
                    self.map = SortedDict({last_power:0})'''
    def decimate(self, format, unc=None, zeropadding=True, sign=True, units=''):
        '''
        returns string of all digits in given format {spacing, spacer, decimal},
        with unc=_Number for embedded uncertainty, and optional leading/trailing zeros & sign
        '''
        top = self.max_power()
        bot = self.min_power()
        if zeropadding:
            top = max(top, 0)
            bot = min(bot, 0)
        if self.zero and not unc and top > 0:
            top = 0
        output = []
        if sign and self.negative:
            output.append('-')
        for p in range(top, bot - 1, -1):
            try:
                output.append(str(self.map[p]))
            except:
                output.append('0')
            if p == self.min_power() and unc:
                output.append('('+unc.decimate(format, zeropadding=False, sign=False)+')')
            if p != bot:
                if p == 0:
                    output.append(format['decimal'])
                elif p % format['spacing'] == 0:
                    output.append(format['spacer'])
        return ''.join(output) + units
    @staticmethod
    def _int(num):
        return int(float(num))
    def output(self, output_type):
        '''returns number in given type'''
        no_formatting = {'decimal': '', 'spacer': '', 'spacing': 0.1}
        num = self.decimate(no_formatting, zeropadding=False) or "0"
        output_type = self._int if output_type == int else output_type
        return output_type(f"{num}E{self.min_power()}")
    def __gt__(self, other):
        if self.max_power() > other.max_power():
            return True
        for p in range(self.max_power(), self.min_power() - 1, -1):
            if p not in other.map:
                if not self.map[p]:
                    continue
                return True
            if self.map[p] > other.map[p]:
                return True
            if self.map[p] < other.map[p]:
                return False
        if other.min_power() > self.min_power():
            return False
        return False
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
            prefixes = SortedDict(_major_prefixes+_minor_prefixes)
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

    keys = {'separator', 'separation', 'sep', 'format', 'sigfigs', 's', 'decimals', 'd', 'uncertainty', 'u', 'cutoff', 'spacing', 'spacer', 'decimal', 'output_type', 'output', 'type', 'style', 'prefix', 'exponent', 'notation', 'form', 'crop'}
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
        elif key in {'spacer', 'decimal'}:
            given[key] = str(val)
            given['output_type'] = str
        elif key == 'spacing':
            given['spacing'] = int(val)
            given['output_type'] = str
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
    if not issubclass(given['output_type'], (numbers.Real, Decimal, _Number)):
        given['format'] = {}
        if 'spacer' in given and 'spacing' not in given:
            given['spacing'] = 3
        if 'spacing' in given and 'spacer' not in given:
            given['spacer'] = ","
        for prop in {'decimal', 'spacer', 'spacing'}:
            if prop in given:
                val = given[prop]
                del given[prop]
            elif prop in _manual_settings:
                val = _manual_settings[prop]
            else:
                val = _default_settings[prop]
            given['format'][prop] = val
    for prop in ['separator', 'prefix', 'exponent']:
        if prop in given:
            continue
        elif prop in _manual_settings:
            given[prop] = _manual_settings[prop]
        else:
            given[prop] = _default_settings[prop]

    return given
def _num_parse(num):
    '''Private function for use only in round()'s _arguments_parse() function:
    Translates given number of any type into returned _Number data structure

    Parsing Algorythm [O(N)]:
    - convert to string
    - characters are analyzed sequentially in a KMP-like state graph. ie:
       number: -325.7854E-5 
       state:  ABBBBCCCCDEE
    - ValueError is raised if input number cannot be deciphered
    '''
    global number, i, n, negative_exp, exp
    number = _Number()
    i = 0
    n = 0
    negative_exp = False
    exp = 0

    if type(num) == type(number):
        return deepcopy(num)
    if num is None:
        warn('no number provided, assuming zero (0)', stacklevel=_warn_stacklevel(4))
        number.map[0] = 0
        number.zero = True
        return number
    if num != num:
        warn('given input is not a number (NaN)')
        number.nan = True
        number.map['NaN'] = num
        return number
    num = str(num)

    digits = set([str(a) for a in range(10)])
    exponents = set(['E', 'e', 'D', 'd', 'Q', 'q'])

    def A(num):
        global number, i, n
        i += 1
        if not num or num in '.-+':
            warn('no number provided, assuming zero (0)', stacklevel=_warn_stacklevel(4))
            number.map[0] = 0
            number.zero = True
            return None
        elif num[0] in exponents:
            warn('no number provided, assuming zero (0)', stacklevel=_warn_stacklevel(4))
            number.map[0] = 0
            number.zero = True
            D(num[1:])
        elif num[0] in '+-':
            number.set_sign(num[0])
            B(num[1:])
        elif num[0] in '.':
            C(num[1:])
        elif num[0] in digits:
            n += 1
            number.map[-n] = int(num[0])
            B(num[1:])
        else:
            raise ValueError(f'parsing failed: invalid input Character "{num[0]}" (position {i}, state A)')
    def B(num):
        global number, i, n
        i += 1
        if not num:
            number.increment_power_by(n)
            return None
        elif num[0] in exponents:
            number.increment_power_by(n)
            D(num[1:])
        elif num[0] in '.':
            number.increment_power_by(n)
            n = 0
            C(num[1:])
        elif num[0] in digits:
            n += 1
            number.map[-n] = int(num[0])
            B(num[1:])
        else:
            raise ValueError(f'parsing failed: invalid Character "{num[0]}" (position {i}, state B)')
    def C(num):
        global number, i, n
        i += 1
        if not num:
            return None
        elif num[0] in exponents:
            D(num[1:])
        elif num[0] in digits:
            n += 1
            number.map[-n] = int(num[0])
            C(num[1:])
        else:
            raise ValueError(f'parsing failed: invalid Character "{num[0]}" (position {i}, state C)')
    def D(num):
        global i, negative_exp, exp
        
        i += 1
        if not num:
            warn('exponent expected but not provided', stacklevel=_warn_stacklevel(4))
            return None
        elif num[0] in '+-':
            if num[0] == '-':
                negative_exp = True
            if not num[1:]:
                warn('exponent expected but not provided', stacklevel=_warn_stacklevel(4))
            exp = 0
            E(num[1:])
        elif num[0] in digits:
            exp = int(num[0])
            E(num[1:])
        else:
            raise ValueError(f'invalid Character "{num[0]}" (position {i}, state D)')
    def E(num):
        global number, i, exp
        i += 1
        if not num:
            sign = 1
            if negative_exp:
                sign = -1
            number.increment_power_by(sign*exp)
            return None
        elif num[0] in digits:
            exp = 10*exp + int(num[0])
            E(num[1:])
        else:
            raise ValueError(f'invalid Character "{num[0]}" (position {i}, state E)')

    A(num)

    p = number.max_power()
    while p in number.map and number.map[p] == 0:
        del number.map[p]
        p -= 1

    if not number.map:
        number.map[0] = 0
        number.zero = True

    return number

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
        round('2.675', '0.00197') => '2.675 ± 0.002'
        round('123456.789099', '-1.15E-4', output='Drake') => '123 456.789 10(12)

    For detailed usage instructions see https://pypi.org/project/sigfig/
    '''
    if not args:
        warn("no input number given, nothing to return", stacklevel=_warn_stacklevel(2))
        return None
    given = _arguments_parse(args, kwargs)
    num = given['num']

    if num.nan:
        return num.map['NaN']
    if 'decimals' in given:
        num.round_by_decimals(given['decimals'])
    elif 'sigfigs' in given:
        if given['sigfigs'] > len(num.map):
            warn(
                f"{given['sigfigs']} significant figures requested from number with only {len(num.map)} significant figures",
                stacklevel=_warn_stacklevel(2)
            )
        last_power = num.max_power() - given['sigfigs'] + 1
        num.round_by_decimals(-last_power)
        while len(num.map) > given['sigfigs']:
            del num.map[num.min_power()]
    elif 'uncertainty' in given:
        num.has_uncertainty = True
        if 'cutoff' in given:
            cutoff = str(given['cutoff'])
        elif 'cutoff' in _manual_settings:
            cutoff = str(_manual_settings['cutoff'])
        else:
            cutoff = str(_default_settings['cutoff'])
        unc = round(given['uncertainty'], sigfigs=len(cutoff), output='map')
        cut = _num_parse(cutoff + 'E' + str(unc.min_power()))
        if unc > cut:
            unc = round(given['uncertainty'], sigfigs=len(cutoff)-1, output='map')
            if unc.map[unc.max_power()] == 1:
                unc.map[unc.max_power() - 1] = 0
        num.round_by_decimals(-unc.min_power())

    if given['prefix']:
        power_shift = num.prefixify(given['prefix'], given['exponent'])
        if 'uncertainty' in given:
            unc.increment_power_by(power_shift)

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
    
    if 'uncertainty' in given and given['separator'] == 'brackets' and unc.min_power() > 0 and 'external_brackets' not in given:
        return num.decimate(given['format'], unc=unc)

    output = num.decimate(given['format'])
    units = num.prefix if given['prefix'] else ''

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
