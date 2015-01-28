#!/usr/bin/env python
# Copyright (C) 2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.

"""
Functions for finding rotations and periodicities of a list of objects. In
python we describe the transformation lst -> [lst.pop()] + lst as a cyclic
rotation of a list, or simply a rotation. The minimal number of nonzero
rotations required for these to compare equal is called the periodicity.

This module contains two different functions for finding a list's periodicity:
one straightforward, and one much more complicated, but presumably more
efficient. It also provides a function for finding the lexicographically
minimal rotation of a list.
"""


import unittest
import collections

import factorization

def periodicity_seed(necklace):
    """
    A faster way of finding the periodicity of a list that avoids work duplication by not repeatedly comparting the first elements of a list.
    """
    necklace = list(necklace)
    n = len(necklace)
    if n in [0, 1]:
        return n
    l = p = 1
    while p != n:
        while not factorization.isdivisor(l, n):
            l += 1
        p = l
        seed = necklace[:p]
        stopit = False
        for repstart in range(l, n, l):
            for ind, val in enumerate(seed):
                l += 1
                if val != necklace[repstart + ind]:
                    stopit = True
                    break
            if stopit:
                break
        else:
            break
    return len(seed)


def periodicity_rotation(cycle):
    """
    Find the "periodicity" of a list; i.e. the number of its distinct cyclic
    rotations. To do this, represent the cycle as a queue, and rotate the queue
    by the divisors of its length until they are equal. The first occurance of
    this is the period.
    """
    orig = collections.deque(cycle)
    cycle = collections.deque(cycle)
    period_prev = 0
    for period in factorization.divisors(len(cycle)):
        cycle.rotate(period-period_prev)
        period_prev = period
        if orig == cycle:
            return period

periodicity = periodicity_seed


def cycle_degeneracy(cycle):
    return len(cycle)//periodicity(cycle)


def smallest_rotation(lst):
    """Return the lexicographically smallest rotation of a list."""
    minrot = list(lst)
    cycle = collections.deque(lst)
    for I in range(len(lst)-1):
        cycle.rotate()
        if minrot > list(cycle):
            minrot = list(cycle)
    return list(minrot)


class RotationTests(unittest.TestCase):
    periods = []
    lists = []

    N = 20
    for n in range(1, N+1):
        for d in factorization.divisors(n):
            periods.append(d)
            lists.append(([0]+[1]*(d-1))*(n//d))

    s1 = [0, 0, 0, 2]
    s2 = s1*3 + [1, 1, 1, 4]
    s3 = s2*2 + [1, 1, 1, 5]
    s4 = s3*3 + [1, 1, 1, 6]
    s = s4*4

    periods.append(112)
    lists.append(s)

    t1 = [(1, 2), ]*3+[(1, 1)]
    t2 = t1*3 + [(1, 4, 3)]*3 + [(1, )]
    t3 = t2*2 + [(2, )]*3 + [(1, 4, 3)]
    t4 = t3*3 + [(3, )]*3+[(1, 2)]
    t = t4*4

    periods.append(112)
    lists.append(t)

    periods.append(1)
    lists.append([(1, 2), (1, 2)])
    periods.append(2)
    lists.append([(1, 2), (1, )])

    tail = [(1, 2), (1, ), (1, 2), (1, ), (1, )]
    periods.append(5)
    lists.append(tail)

    agreeing_tail = [(1, 2), (1, ), (1, 2), (1, ), (1, 2)]
    periods.append(5)
    lists.append(agreeing_tail)

    def testPeriodicities(self):
        for period, lst in zip(self.periods, self.lists):
            self.assertEqual(period, periodicity_rotation(lst))
            self.assertEqual(period, periodicity_seed(lst))

    def testMinimalRotations(self):
        for lst in self.lists:
            self.assertTrue(smallest_rotation(lst) <= lst)
            if lst[0] != min(lst):
                self.assertTrue(smallest_rotation(lst) < lst)


if __name__ == '__main__':
    unittest.main()
