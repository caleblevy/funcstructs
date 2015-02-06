#!/usr/bin/env python
# Copyright (C) 2014-2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.

"""
Multisets is a utilities module for performing miscellaneous operations and
finding information about sets and multisets: breaking up multisets, getting
elements of a set, and counting ways to represent them assuming certain
properties are equivalent.
"""

import bags
from functools import reduce
from math import factorial
from operator import mul
import unittest

from sympy.utilities.iterables import multiset_partitions

prod = lambda iterable: reduce(mul, iterable, 1)
factorial_prod = lambda iterable: prod(factorial(I) for I in iterable)
nCk = lambda n, k: factorial(n)//factorial(k)//factorial(n-k)


class Multiset(bags.frozenbag):

    def __repr__(self):
        """Override repr with my preferred format."""
        if self._size == 0:
            return self.__class__.__name__+"({})"
        elements = super(bags.frozenbag, self).__str__()
        return self.__class__.__name__+"("+elements+")"

    def __str__(self):
        return repr(self)

    def split(self):
        """Splits the multiset into element-multiplicity pairs."""
        y = list(self._dict)
        d = [self._dict[el] for el in y]
        return y, d

    def degeneracy(self):
        """Number of different representations of the same multiset."""
        y, d = self.split()
        return factorial_prod(d)

    def partitions(self):
        """
        Yield partitions of a multiset, each one being a multiset of multisets.
        """
        return multiset_partitions(list(self))


class MultisetTests(unittest.TestCase):

    def testSplitSet(self):
        """Test that we can split the multiset into elements and counts"""
        abra = Multiset("abracadabra")
        y, d = abra.split()
        for el in y:
            self.assertEqual(abra.count(el), d[y.index(el)])

    def testMultisetDegeneracy(self):
        abra = Multiset("abracadabra")
        self.assertEqual(120*2*2, abra.degeneracy())

if __name__ == '__main__':
    unittest.main()

