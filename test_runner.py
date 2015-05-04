"""Run all unit tests."""
from __future__ import print_function

import unittest

test_finder = unittest.TestLoader()
test_runner = unittest.TextTestRunner()


if __name__ == '__main__':
    test_finder.discover('.')
    print("\nTesting endofunction_structures:")
    test_runner.run(test_finder.discover('./endofunction_structures'))
    print("\nTesting funcgraphs:")
    test_runner.run(test_finder.discover('./funcgraphs'))
    print("\nTesting prototypes:")
    test_runner.run(test_finder.discover('./prototyping', pattern='*.py'))
