#!/usr/bin/env python
# Copyright (C) 2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.

"""Multiset combinations.

A commutative ring with identity consisting of collections of multisets. The
addition is defined by union of two elements. The multiplication is the union
of all pairwise unions of elements. """


import itertools
import collections
import unittest

from . import multiset
from . import polynomials


class MultiCombo(object):
    """ Built to feed into a symmetric monomial polynomial and expand into
    lists of multisets. """

    def __init__(self, iterable=None):
        self.cpart = collections.Counter()
        if iterable is not None:
            if hasattr(iterable, 'elements'):
                iterable = iterable.elements()
            if hasattr(iterable, '__iter__'):
                for el in iterable:
                    if not hasattr(el, '__iter__'):
                        el = [el]
                    self.cpart.update([multiset.Multiset(el)])
            else:
                self.cpart.update([multiset.Multiset([iterable])])

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.cpart == other.cpart
        return False

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return type(self).__name__+'(%s)' % str(list(self.cpart))

    def __str__(self):
        set_str = str(multiset.Multiset(self.cpart))[1:-1]
        if not self.cpart:
            set_str = '{}'
        return type(self).__name__+'(%s)' % set_str

    def __iter__(self):
        return (el for el in self.cpart.elements())

    def __add__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(self.cpart + other.cpart)
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
                    lol.append(list(l1)+list(l2))
            return self.__class__(lol)
        elif other == 1:
            return self
        elif other == 0:
            return 0
        raise TypeError("Cannot perform arithmetic with %s and %s" % (
            self.__class__.__name__,
            other.__class__.__name__)
        )

    def __rmul__(self, other):
        return self * other

    def __pow__(self, n):
        cp = 1
        for i in range(n):
            cp *= self
        return cp


def multisets_with_multiplicities(elems, multiplicities):
    x = [MultiCombo(el) for el in elems]
    for mset in polynomials.monomial_symmetric_polynomial(x, multiplicities):
        yield multiset.Multiset(mset)


class SetListTests(unittest.TestCase):

    def test_init(self):
        self.assertEqual(MultiCombo(1), MultiCombo([1]))
        self.assertEqual(MultiCombo(1), MultiCombo([[1]]))
        self.assertEqual(MultiCombo(1), MultiCombo(MultiCombo(1)))
        self.assertEqual(MultiCombo([1, 2]), MultiCombo([[1], [2]]))

        self.assertEqual(MultiCombo([1, 2]), MultiCombo([[1], 2]))
        self.assertEqual(MultiCombo([2, 1]), MultiCombo([1, 2]))

    def test_addition(self):
        """Test the addition obeys ring properties"""
        self.assertEqual(
            MultiCombo([1, 2, 2, 3]),
            MultiCombo([1, 2])+MultiCombo([2, 3])
        )
        # Ensure the addition is abelian
        self.assertEqual(
            MultiCombo([1, 2]) + MultiCombo([3, 4]) + MultiCombo([5, [6, 7]]),
            MultiCombo([[7, 6], 5]) + MultiCombo([2, 1]) + MultiCombo([3, 4])
        )
        # Test that zero is additive identity
        self.assertEqual(MultiCombo([1, 2]), MultiCombo([1, 2]) + 0)
        self.assertEqual(MultiCombo([1, 2]) + 0, 0 + MultiCombo([1, 2]))

    def test_multiplication(self):
        """Test that the multiplication is well defined"""
        self.assertEqual(
            MultiCombo([1, 2]) * MultiCombo([3, 4]),
            MultiCombo([[1, 3], [1, 4], [2, 3], [2, 4]])
        )
        # Test multiplicative identity
        self.assertEqual(MultiCombo(1), MultiCombo(1) * 1)
        self.assertEqual(MultiCombo(1), 1 * MultiCombo([1]))
        # Test 0
        self.assertEqual(0, 0*MultiCombo([1]))
        self.assertEqual(0, MultiCombo([1])*0)
        # Test the multiplication is commutative
        a = MultiCombo([1, 1, 2])
        b = MultiCombo([1, [1, 2]])
        c = MultiCombo([1, 2, 3])
        self.assertEqual(a*b, b*a)
        self.assertEqual(a*c, c*a)
        self.assertEqual(b*c, c*b)

    def test_pow(self):
        self.assertEqual(
            MultiCombo([[1, 1], [2, 2]]) ** 3,
            MultiCombo([
                [1, 1, 1, 1],
                [2, 2, 2, 2],
                [1, 1, 2, 2],
                [2, 2, 1, 1]
            ]) * MultiCombo([[1, 1], [2, 2]])
        )
        a = MultiCombo([[1, 1, 2], [3, 3, 4], [5], 5])
        self.assertEqual(a*a*a*a, a**4)

    def test_distributivity(self):
        """Test the multiplication is left and right distributive"""
        a = MultiCombo([1, 1, 2])
        b = MultiCombo([1, 2])
        c = MultiCombo([3, 4])
        self.assertEqual(a*(b+c), a*b + a*c)
        self.assertEqual((a+b)*c, a*c + b*c)

    def test_msp(self):
        """ Ensure MultiCombo satisfies the requirements of a symmetric
        monomial polynomial. """
        self.assertEqual(
            MultiCombo(multisets_with_multiplicities([2, 3, 14], [2, 2])),
            MultiCombo([[2, 2, 3, 3], [2, 2, 14, 14], [3, 3, 14, 14]])
        )


if __name__ == '__main__':
    unittest.main()
