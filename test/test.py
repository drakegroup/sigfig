'''Sigfig testing module

Requires the following semi-colon separated CSV files:
  - test_equality.csv
  - test_warning.csv
  - test_depreciated.csv
  - test_exception.csv
'''

from decimal import Decimal, Inexact, Rounded, localcontext
from warnings import warn, filterwarnings, resetwarnings
from inspect import currentframe, getframeinfo
from runpy import run_path
from unittest.mock import patch
import unittest, csv

from numpy import float64, float32, int64, int32, nan, isnan

from sys import path, exit
from pathlib import Path
path.insert(0, str(Path(__file__).parent / "../sigfig"))
from sigfig import round, _num_parse, roundit, round_unc, round_sf
from sigfig import ROUND_05UP, ROUND_CEILING, ROUND_DOWN, ROUND_FLOOR, ROUND_HALF_DOWN, ROUND_HALF_EVEN, ROUND_HALF_UP, ROUND_UP

def function_parse(func):
    '''Comprehends string representation of function call to
    return (function name, arguments, keyword arguments) tuple
    
    *Unable to parse commas (in lists, strings, tuples) ie. round((1,2),1)... use recursion'''
    name, parameters = func.split('(', 1)
    parameters = parameters[:-1].split(',')
    args, kwargs = [], {}
    for p in parameters:
        p = p.strip()
        if '=' in p:
            key, val = p.split('=')
            kwargs[key.strip()] = eval(val.strip())
        else:
            args.append(eval(p))
    return name, args, kwargs

class KnownGood(unittest.TestCase):
    '''Compares each run of round() with expected output'''
    def __init__(self, args, kwargs, output):
        super(KnownGood, self).__init__()
        self.args = args
        self.kwargs = kwargs
        self.output = output
    def runTest(self):
        if type(self.output) == float:
            self.assertAlmostEqual(round(*self.args, **self.kwargs), self.output)
        else:
            self.assertEqual(round(*self.args, **self.kwargs), self.output)

class KnownGrtr(unittest.TestCase):
    '''Runs each test of _Number's ">" operator'''
    def __init__(self, x, y, z):
        super(KnownGrtr, self).__init__()
        self.x = x
        self.y = y
        self.z = z
    def runTest(self):
        self.assertEqual(_num_parse(self.x) > _num_parse(self.y), self.z)

class KnownWarn(unittest.TestCase):
    '''Compares each run of round() with expected output & proper warning message'''
    def __init__(self, args, kwargs, output):
        super(KnownWarn, self).__init__()
        self.args = args
        self.kwargs = kwargs
        self.output = output
    def runTest(self):
        with self.assertWarns(UserWarning) as warn_context:
            round(*self.args,**self.kwargs)
            line_number_hack = getframeinfo(currentframe()).lineno
        self.assertEqual(__file__, warn_context.filename, 'Warning raised in wrong file')
        self.assertEqual(line_number_hack-1, warn_context.lineno, 'Warning not getting the right line number')
        filterwarnings("ignore")
        if type(self.output) == float:
            self.assertAlmostEqual(round(*self.args, **self.kwargs), self.output)
        else:
            self.assertEqual(round(*self.args, **self.kwargs), self.output)
        resetwarnings()

class KnownWarnLoud(unittest.TestCase):
    '''Compares each run of round() with expected warning message without checking proper output'''
    def __init__(self, args, kwargs, output):
        super(KnownWarnLoud, self).__init__()
        self.args = args
        self.kwargs = kwargs
        self.output = output
    def runTest(self):
        self.assertWarns(UserWarning,round,*self.args,**self.kwargs)

class TestType(unittest.TestCase):
    '''Tests exception raise for invalid input type'''
    def runTest(self):
        self.assertRaises(TypeError, round, (1,2), 1)

class TestNaN(unittest.TestCase):
    '''Tests NaN behavior for round()'''
    def __init__(self, args, kwargs):
        super(TestNaN, self).__init__()
        self.args = args
        self.kwargs = kwargs
    def runTest(self):
        self.assertWarns(UserWarning,round,*self.args,**self.kwargs)
        filterwarnings("ignore")
        assert(isnan(round(*self.args, **self.kwargs)))
        resetwarnings()

class KnownDepr(unittest.TestCase):
    '''Compares each run of round() with expected output for depreciated usages'''
    def __init__(self, func, output):
        super(KnownDepr, self).__init__()
        self.func_call = func
        self.func_name, self.func_args, self.func_kwargs = function_parse(func)
        self.output = output
    def runTest(self):
        self.assertWarns(DeprecationWarning, eval(self.func_name), *self.func_args, **self.func_kwargs)
        filterwarnings("ignore")
        self.assertEqual(eval(self.func_call), eval(self.output))
        resetwarnings()

class KnownExcp(unittest.TestCase):
    '''Compares each improper run of round() with expected exception'''
    def __init__(self, func, result):
        super(KnownExcp, self).__init__()
        self.func_call = func
        self.func_name, self.func_args, self.func_kwargs = function_parse(func)
        self.result = result
    def runTest(self):
        self.assertRaises(eval(self.result), eval(self.func_name), *self.func_args, **self.func_kwargs)

class DecimalRounding(unittest.TestCase):
    def test_decimal_context_independence(self):
        with localcontext() as context:
            context.prec = 2
            context.rounding = ROUND_DOWN
            context.Emin = -2
            context.Emax = 2
            context.traps[Inexact] = True
            context.traps[Rounded] = True
            context.clear_flags()
            original = context.copy()
            self.assertEqual(round('12345.675', decimals=2), '12345.68')
            self.assertEqual(round('12345.675', decimals=2, mode=ROUND_DOWN), '12345.67')
            self.assertEqual(round('2.75', decimals=1, mode=ROUND_HALF_EVEN), '2.8')
            self.assertEqual(round(2.675, decimals=2), 2.68)
            self.assertEqual(round('9.995', sigfigs=3), '10.0')
            self.assertEqual(round('12345.6745', '0.005', sep=tuple), ('12345.675', '0.005'))
            self.assertEqual(round('123456789.123456789', notation='sci'), '1.23456789123456789E8')
            self.assertEqual(round('123456789.123456789', prefix=True), '123.456789123456789M')
            for attribute in ('prec', 'rounding', 'Emin', 'Emax', 'traps', 'flags'):
                with self.subTest(attribute=attribute):
                    self.assertEqual(getattr(context, attribute), getattr(original, attribute))

class TestWarningFailures(unittest.TestCase):
    def runTest(self):
        cases = [
            KnownWarn((2.1, 7), {}, 2.1),
            KnownWarnLoud((2.1, 7), {}, 2.1),
            TestNaN((nan, 1), {}),
            KnownDepr('round_sf(2.1, 1)', '2.0'),
        ]
        for case in cases:
            with self.subTest(case=type(case).__name__):
                with patch('sigfig.warn'):
                    result = unittest.TestResult()
                    case.run(result)
                self.assertEqual(len(result.failures), 1)
                self.assertEqual(result.errors, [])
                self.assertIn('Warning not triggered', result.failures[0][1])

class TestRunner(unittest.TestCase):
    def runTest(self):
        for outcome in ('success', 'failures', 'errors'):
            with self.subTest(outcome=outcome):
                result = unittest.TestResult()
                if outcome != 'success':
                    getattr(result, outcome).append((self, 'expected ' + outcome))
                with patch.object(unittest.TextTestRunner, 'run', return_value=result):
                    with self.assertRaises(SystemExit) as context:
                        run_path(__file__, run_name='__main__')
                self.assertEqual(context.exception.code, 0 if outcome == 'success' else 1)

def suite():
    '''Function containing a suite of all test cases for sigfig module'''
    def cases(filename):
        with open(Path(__file__).parent / filename, newline='') as f:
            line = 0
            for case in csv.reader(f, delimiter=';'):
                line += 1
                try:
                    case = [eval(case[0].replace('ï»¿','')),
                            eval(case[1]),
                            eval(case[2].replace('Â',''))]
                except:
                    print('problem on line %d of %s' % (line, filename))
                    continue
                yield case
    
    suite = unittest.TestSuite()
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(DecimalRounding))
    suite.addTest(TestWarningFailures())
    suite.addTest(TestRunner())
    eq_cases = cases('test_equality.csv')
    suite.addTests(KnownGood(args, kwargs, output) for args, kwargs, output in eq_cases)
    class_cases = [[30, 3, True], [1.2, 1, True], [1.0, 1, False], [1, 1.0, False], [1, 1, False]]
    suite.addTests(KnownGrtr(x, y, z) for x, y, z in class_cases)
    warn_cases = cases('test_warning.csv')
    suite.addTests(KnownWarn(args, kwargs, output) for args, kwargs, output in warn_cases)
    warn_loud_cases = cases('test_warn_unmutable.csv')
    suite.addTests(KnownWarnLoud(args, kwargs, output) for args, kwargs, output in warn_loud_cases)
    suite.addTest(TestType())
    nan_cases = [[(nan, 1), {}], [(nan,), {'d':3}], [(nan,), {'s':4}], [(nan,), {'u':4.0}]]
    suite.addTests(TestNaN(*case) for case in nan_cases)
    def general_cases(filename):
        with open(Path(__file__).parent / filename, newline='') as f:
            line = 0
            for case in csv.reader(f, delimiter=';'):
                line += 1
                try:
                    case = [case[0].replace('ï»¿',''),
                            case[1]]
                except:
                    print('problem on line %d of %s' % (line, filename))
                    continue
                yield case
    depreciated_cases = general_cases('test_depreciated.csv')
    suite.addTests(KnownDepr(func, output) for func, output in depreciated_cases)
    exception_cases = general_cases('test_exception.csv')
    suite.addTests(KnownExcp(func, result) for func, result in exception_cases)
    # test creating _Number instance & setting sign = '*'
    # test warnings for round(decimals=2)
    # either add a minor_prefixes test or move it to a feature branch
    # test setting a _manual_settings change or move it to feature branch
    return suite

if __name__ == '__main__':
    exit(not unittest.TextTestRunner().run(suite()).wasSuccessful())
