#!/usr/bin/env python
# Copyright (C) 2014-2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.

"""
Two common kinds of problem in combinatorics are enumeration and counting. In
theory we may view counting as a strict subproblem of enumeration, since
enumerating all elements in a set necessarily allows us to count them.

In practice, there are many tricks one may use to count the number of objects
in a set while performing far less work than listing the elements directly.
This module collects efficient ways of counting endofunction-related objects
without direct enumeration.
"""

from multiset import split_set, prod
from iteration import tuple_partitions
from fractions import Fraction
from primes import divisors
from integerroots import isqrt

from itertools import chain
from math import factorial

import unittest


def funcstruct_count(n):
    """
    Count the number of endofunction structures on n nodes. Iterates over the
    tuple representation of partitions using the formula featured in
        De Bruijn, N.G., "Enumeration of Mapping Patterns", Journal of
        Combinatorial Theory, Volume 12, 1972.

    See the papers directory for the original reference.
    """
    tot = 0
    for b in tuple_partitions(n):
        product_terms = []
        for I in range(1, len(b)+1):
            s = 0
            for J in divisors(I):
                s += J*b[J-1]
            s **= b[I-1]
            s *= Fraction(I, 1)**(-b[I-1])/factorial(b[I-1])
            product_terms.append(s)
        tot += prod(product_terms)
    return int(tot)


def rooted_treecount_upto(N):
    """
    Returns the number of rooted tree structures on n nodes. Algorithm featured
    without derivation in
        Finch, S. R. "Otter's Tree Enumeration Constants." Section 5.6 in
        "Mathematical Constants", Cambridge, England: Cambridge University
        Press, pp. 295-316, 2003.
    """
    if N == 0:
        return [0]
    if N == 1:
        return [0, 1]
    T = [0, 1]+[0]*(N-1)
    for n in range(2, N+1):
        for I in range(1, n):
            s = 0
            for d in divisors(I):
                s += T[d]*d
            s *= T[n-I]
            T[n] += s
        T[n] //= (n-1)
    return T

rooted_treecount = lambda n: rooted_treecount_upto(n)[-1]


def partition_numbers_upto(N):
    """
    Uses Euler's Pentagonal Number Theorem to count partition number using the
    previous terms. The sum is taken over O(sqrt(n)) terms on each pass, so the
    algorithm runs in O(n**3/2)

    See the Knoch paper in papers folder for a proof of the theorem.
    """
    if N == 0:
        return [1]
    P = [1]+[0]*N
    for n in range(1, N+1):
        k_max = (isqrt(24*n+1)-1)//6
        k_min = -((isqrt(24*n+1)+1)//6)
        for k in chain(range(k_min, 0), range(1, k_max+1)):
            P[n] += (-1)**abs((k-1)) * P[n-k*(3*k+1)//2]
    return P

partition_number = lambda n: partition_numbers_upto(n)[-1]


class CounterTest(unittest.TestCase):

    def testEndofunctionStructureCount(self):
        A001372 = [1, 1, 3, 7, 19, 47, 130, 343, 951, 2615, 7318, 20491, 57903]
        for n, count in enumerate(A001372):
            self.assertEqual(count, funcstruct_count(n))

    def testTreeCounts(self):
        A000081 = [0, 1, 1, 2, 4, 9, 20, 48, 115, 286, 719, 1842, 4766, 12486]
        self.assertEqual(A000081, rooted_treecount_upto(len(A000081)-1))

    def testPartitionNumbers(self):
        A000041 = [1, 1, 2, 3, 5, 7, 11, 15, 22, 30, 42, 56, 77, 101, 135]
        self.assertEqual(A000041, partition_numbers_upto(len(A000041)-1))


if __name__ == '__main__':
    unittest.main()
