"""Run all unit tests."""
from __future__ import print_function

import importlib
import os
import pkgutil
import sys
import unittest

test_dir = os.path.dirname(os.path.abspath(__file__))
# sys.path hackery which seems to make this run in python and python3
sys.path.insert(0, os.path.dirname(os.path.abspath(test_dir)))

not_for_testing = ["__main__", "benchmarks", "testcases"]

numpy_dependant = []
matplotlib_dependant = []

suite = unittest.TestSuite()

# "Is there a standard way to list names of Python modules in a package?" at
# http://stackoverflow.com/a/1310912/3349520
for _, mod, _ in pkgutil.walk_packages([test_dir]):
    if any(name in mod for name in not_for_testing):
        continue
    try:
        # "import module from string variable" at
        # http://stackoverflow.com/a/8719100/3349520
        importlib.import_module(mod)
    except ImportError as e:
        error_message = str(e)
        if 'numpy' in error_message:
            numpy_dependant.append(mod)
        elif 'matplotlib' in error_message:
            matplotlib_dependant.append(mod)
        else:
            raise
    else:
        # "how to run all Python unit tests in a directory" at
        # http://stackoverflow.com/a/1732477/3349520
        suite.addTest(unittest.defaultTestLoader.loadTestsFromName(mod))


if numpy_dependant:
    print("\nThe following tests require numpy, and will be skipped:\n")
    for test in numpy_dependant:
        print('\t%s' % test)
    print()

if matplotlib_dependant:
    print("\nThe following tests require matplotlib, and will be skipped:\n")
    for test in matplotlib_dependant:
        print('\t%s' % test)
    print()


if __name__ == '__main__':
    # "Unit test script returns exit code = 0 even if tests fail" at
    # http://stackoverflow.com/q/24972098/3349520
    result = not unittest.TextTestRunner().run(suite).wasSuccessful()
    sys.exit(result)
