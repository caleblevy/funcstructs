#!/usr/bin/env python
# Copyright (C) 2014-2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.

"""A representation of the ring of multiset partitions."""

import itertools
import unittest

import sympy

from . import multiset
from . import productrange
from . import polynomials
from . import necklaces


class ListSet(object):
    """ Built to feed into a symmetric monomial polynomial and expand into
    lists of multisets. """
    def __init__(self, lol=None):
        if lol is None:
            self.lol = []
        elif hasattr(lol, '__iter__'):
            for el in lol:
                if hasattr(el, '__iter__'):
                    continue
                self.lol = [[e] for e in lol]
                break
            else:
                self.lol = list(lol)
        else:
            self.lol = [[lol]]

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.lol == other.lol
        return False

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return self.__class__.__name__+'(%s)' % str(self.lol)

    def __iter__(self):
        return (el for el in self.lol)

    def __add__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(self.lol + other.lol)
        elif other == 0:
            return self
        raise TypeError("Cannot perform arithmetic with %s and %s" % (
            self.__class__.__name__,
            other.__class__.__name__)
        )

    def __radd__(self, other):
        return self + other

    def __mul__(self, other):
        if isinstance(other, self.__class__):
            lol = []
            for l1 in self:
                for l2 in other:
                    lol.append(l1+l2)
            return self.__class__(lol)
        elif other == 1:
            return self ** 1
        elif other == 0:
            return 0
        raise TypeError("Cannot perform arithmetic with %s and %s" % (
            self.__class__.__name__,
            other.__class__.__name__)
        )

    def __rmul__(self, other):
        return self * other

    def multiform(self):
        for l in self:
            yield multiset.Multiset(l)

    def __pow__(self, n):
        return self.__class__([el*n for el in self])


def multisets_from_elements_with_multiplicities(elems, multiplicities):
    x = [ListSet(el) for el in elems]
    for mset in polynomials.monomial_symmetric_polynomial(x, multiplicities):
        yield multiset.Multiset(mset)

for mset in multisets_from_elements_with_multiplicities([2, 3, 14], [2, 2]):
    print mset

print necklaces.FixedContentNecklaces([1, 2, 1, 2]).count_by_period()


x = [sympy.symbols('x1'), sympy.symbols('x2')]
print x
print polynomials.monomial_symmetric_polynomial(x, [2, 1])
periods = [2, 3, 14]
x = [ListSet(p) for p in periods]
print polynomials.monomial_symmetric_polynomial(x, [2, 2])


class SetListTests(unittest.TestCase):

    def test_init(self):
        self.assertEqual(ListSet(1), ListSet([1]))
        self.assertEqual(ListSet(1), ListSet([[1]]))
        self.assertEqual(ListSet(1), ListSet(ListSet(1)))
        self.assertEqual(ListSet([1, 2]), ListSet([[1], [2]]))

        self.assertNotEqual(ListSet([1, 2]), ListSet([[1], 2]))
        self.assertNotEqual(ListSet([2, 1]), ListSet([1, 2]))

    def test_add(self):
        self.assertEqual(
            ListSet([1, 2, 2, 3]),
            ListSet([1, 2])+ListSet([2, 3])
        )
        self.assertEqual(
            ListSet([1, 2]),
            ListSet([1, 2]) + 0
        )
        self.assertEqual(
            ListSet([1, 2]) + 0,
            0 + ListSet([1, 2])
        )

    def test_mul(self):
        self.assertEqual(
            ListSet([1, 2]) * ListSet([3, 4]),
            ListSet([[1, 3], [1, 4], [2, 3], [2, 4]])
        )
        self.assertNotEqual(
            ListSet([1, 2]) * ListSet([3, 4]),
            ListSet([[3, 1], [1, 4], [2, 3], [2, 4]])
        )
        self.assertEqual(
            ListSet(1),
            ListSet(1) * 1
        )
        self.assertEqual(
            ListSet(1),
            1 * ListSet([1])
        )
        self.assertEqual(0, 0*ListSet([1]))
        self.assertEqual(0, ListSet([1])*0)

    def test_pow(self):
        self.assertEqual(
            ListSet([[1, 1], [2, 2]]) ** 3,
            ListSet([[1, 1, 1, 1, 1, 1], [2, 2, 2, 2, 2, 2]])
        )

    # def test_distributive(self):
    #     a = ListSet([1, 1, 2])
    #     b = ListSet([1, 2])
    #     c = ListSet([3, 4])
    #     self.assertEqual(a*(b+c), a*b + a*c)
    #     self.assertEqual((a+b)*c, a*c + b*c)


if __name__ == '__main__':
    unittest.main()
