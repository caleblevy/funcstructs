#!/usr/bin/env python
# Copyright (C) 2014-2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.

"""Set Operations.

setops is a module for performing miscellaneous operations on various kinds of
sets: breaking up multisets, getting elements, and finding their images and
preimages under endofunctions. It is a utilities module.

"""

from functools import reduce
from math import factorial
from operator import mul

import unittest

prod = lambda iterable: reduce(mul, iterable, 1)
factorial_prod = lambda iterable: prod(factorial(I) for I in iterable)
nCk = lambda n, k: factorial(n)//factorial(k)//factorial(n-k)


def split_set(partition):
    """Splits a multiset of hashable items into elements and multiplicities."""
    y = list(set(partition))
    d = [partition.count(y[I]) for I in range(len(y))]
    return y, d


def mset_degeneracy(mset):
    """Number of different representations of the same multiset."""
    y, d = split_set(mset)
    return factorial_prod(d)


def get(S):
    """ Get a random element from a set (or any iterable). """
    for x in S:
        return x
    raise ValueError("Cannot retrieve an item from the empty set")


def preimage(f):
    """
    Given an endofunction f defined on S=range(len(f)), returns the preimage of
    f. If g=preimage(f), we have

        g[y]=[x for x in S if f[x]==y],

    or mathematically:

        f^-1(y)={x in S: f(x)=y}.

    Note the particularly close correspondence between python's list
    comprehensions and mathematical set-builder notation.
    """
    S = range(len(f))
    preim = []
    for y in S:
        preim.append([x for x in S if y == f[x]])
    return preim


def imagepath(f):
    """
    Give it a list so that all([I in range(len(f)) for I in f]) and this
    program spits out the image path of f.
    """
    n = len(f)
    cardinalities = [len(set(f))]
    f_orig = f[:]
    card_prev = n
    for it in range(1, n-1):
        f = [f_orig[x] for x in f]
        card = len(set(f))
        cardinalities.append(len(set(f)))
        if card == card_prev:
            cardinalities.extend([card]*(n-2-it))
            break
        card_prev = card
    return cardinalities


class ImagepathTest(unittest.TestCase):

    def testImagepath(self):
        """Check various special and degenerate cases, with right index"""
        self.assertEqual([1], imagepath([0]))
        self.assertEqual([1], imagepath([0, 0]))
        self.assertEqual([1], imagepath([1, 1]))
        self.assertEqual([2], imagepath([0, 1]))
        self.assertEqual([2], imagepath([1, 0]))
        node_count = [2, 3, 5, 15]
        for n in node_count:
            tower = [0] + list(range(n-1))
            cycle = [n-1] + list(range(n-1))
            fixed = list(range(n))
            degen = [0]*n
            self.assertEqual(list(range(n)[:0:-1]), imagepath(tower))
            self.assertEqual([n]*(n-1), imagepath(cycle))
            self.assertEqual([n]*(n-1), imagepath(fixed))
            self.assertEqual([1]*(n-1), imagepath(degen))


if __name__ == '__main__':
    unittest.main()
