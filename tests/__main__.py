"""Run all unit tests."""
from __future__ import print_function

import importlib
import os
import pkgutil
import unittest

# Switch to where the stupid module walker will find them
test_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.dirname(test_dir))


numpy_dependant = []
matplotlib_dependant = []
suite = unittest.TestSuite()


# For the hackery required to do this, please see:
# * "how to run all Python unit tests in a directory"
#   at http://stackoverflow.com/a/1732477/3349520
# * "Is there a standard way to list names of Python modules in a package?"
#   at http://stackoverflow.com/a/1310912/3349520
# * "import module from string variable"
#   at http://stackoverflow.com/a/8719100/3349520


for _, mod, _ in pkgutil.walk_packages([test_dir]):
    if mod == '__main__':
        continue  # do not test the tester
    name = 'tests.' + mod
    try:
        importlib.import_module(name)
    except ImportError as e:
        error_message = str(e)
        if 'numpy' in error_message:
            numpy_dependant.append(mod)
        elif 'matplotlib' in error_message:
            matplotlib_dependant.append(mod)
        else:
            raise
    else:
        suite.addTest(unittest.defaultTestLoader.loadTestsFromName(name))


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
    unittest.TextTestRunner().run(suite)
