#!/usr/bin/env python
# Copyright (C) 2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.

import math
import itertools
import unittest


def arrangement_count(n, b):

    """The total number of ways of evenly dividing a set S with n elements
    into b parts is n!/((n/b)!^b b!) which we can see as follows:

    Take all the permutations of S of which there are n!. We divide them
    into subsequences of length b. If we then disregard ordering each
    selection of subsequences will appear b! times. Each subsequence in
    each permutation of subsequences has (n/b)! representations, and there
    are b independent bins in each selection.

    Each combination of combinations will thus have (n/b)!**b * b! distinct
    representations. """

    return math.factorial(n)//(math.factorial(n//b)**b)//math.factorial(b)


def _evenly_divide(items, b):
    if b == 1:
        yield [frozenset(items)]
    else:
        n = len(items)
        marked_el = (items[0], )
        items = items[1:]
        S = set(items)
        for first_combo in itertools.combinations(items, n//b-1):
            remaining_elements = list(S - set(first_combo))
            for remaining_combos in _evenly_divide(remaining_elements, b-1):
                yield [frozenset(marked_el + first_combo)] + remaining_combos


def evenly_divide(items, b):
    """Evenly split a set of itmes into b parts."""
    items = list(items)
    if len(items) % b:
        raise ValueError("items must divide evenly")
    for division in _evenly_divide(items, b):
        yield frozenset(division)


class LabellingTests(unittest.TestCase):

    split_sets = [(6, 2), (6, 3), (9, 3), (12, 3), (12, 4)]

    def test_division_counts(self):
        """ Check that we produce the correct number of combinations. """
        for n, b in self.split_sets:
            self.assertEqual(arrangement_count(n, b),
                             len(frozenset(evenly_divide(range(n), b))))

    def test_division_uniqueness(self):
        """Make sure each division is a partition of the original set"""
        for n, b in self.split_sets:
            for division in evenly_divide(range(n), b):
                s = set(itertools.chain.from_iterable(division))
                self.assertEqual(n, len(s))


if __name__ == '__main__':
    unittest.main()
