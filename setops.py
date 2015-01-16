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

from functools import reduce
from math import factorial
from operator import mul

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
