'''Sigfig testing module

Requires the following semi-colon separated CSV files:
  - test_equality.csv
  - test_warning.csv
  - test_depreciated.csv
  - test_exception.csv
'''

from decimal import Decimal
from warnings import warn, filterwarnings, resetwarnings
import unittest, csv

from sys import path
path.append('../sigfig')
from sigfig import round, _num_parse, roundit, round_unc, round_sf

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
        self.assertWarns(UserWarning,round,*self.args,**self.kwargs)
        filterwarnings("ignore")
        if type(self.output) == float:
            self.assertAlmostEqual(round(*self.args, **self.kwargs), self.output)
        else:
            self.assertEqual(round(*self.args, **self.kwargs), self.output)
        resetwarnings()

class TestType(unittest.TestCase):
    '''Tests exception raise for invalid input type'''
    def runTest(self):
        self.assertRaises(TypeError, round, (1,2), 1)

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

def suite():
    '''Function containing a suite of all test cases for sigfig module'''
    def cases(filename):
        with open(filename, newline='') as f:
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
    eq_cases = cases('test_equality.csv')
    suite.addTests(KnownGood(args, kwargs, output) for args, kwargs, output in eq_cases)
    class_cases = [[30, 3, True], [1.2, 1, True], [1.0, 1, False], [1, 1.0, False], [1, 1, False]]
    suite.addTests(KnownGrtr(x, y, z) for x, y, z in class_cases)
    warn_cases = cases('test_warning.csv')
    suite.addTests(KnownWarn(args, kwargs, output) for args, kwargs, output in warn_cases)
    suite.addTest(TestType())
    def general_cases(filename):
        with open(filename, newline='') as f:
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
    unittest.TextTestRunner().run(suite())
