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
from collections import deque

from primes import divisors
from iteration import endofunctions


def _patternbreak_index(seed, necklace, start=1):
    """
    When testing for the candidacy of a seed, we test it in sequencial bins of
    width len(seed), and at the first instance of a disagreeing bin, we return
    that index, since the seed must at least contain everythin up to that
    index.
    """
    l = len(seed)
    n = len(necklace)
    for I in range(start, n//l+1):
        if seed != necklace[I*l:(I+1)*l]:
            return l*I
    return n


def periodicity_seed(necklace):
    """
    An arguably faster way of finding the periodicity of a list. Starting with
    the first element, any sublist from which a necklace is built must have at
    least as many elements as there are between the next repetition of the
    first element. This logic repeats until there is a break.
    """
    necklace = list(necklace)
    seed = [necklace[0]]
    n = len(necklace)
    break_ind = 0
    while True:
        break_ind = _patternbreak_index(seed, necklace)
        if break_ind == len(necklace):
            return len(seed)
        l = len(seed)
        seed.extend(necklace[l: break_ind])
        next_terms = []
        for I in range(break_ind, n-l):
            if seed == necklace[I:I+l]:
                seed.extend(next_terms)
                break
            next_terms.append(necklace[I])
        if len(seed) == l:
            return n


def periodicity_rotation(cycle):
    """
    Find the "periodicity" of a list; i.e. the number of its distinct cyclic
    rotations. To do this, represent the cycle as a queue, and rotate the queue
    by the divisors of its length until they are equal. The first occurance of
    this is the period.
    """
    orig = deque(cycle)
    cycle = deque(cycle)
    period_prev = 0
    for period in divisors(len(cycle)):
        cycle.rotate(period-period_prev)
        period_prev = period
        if orig == cycle:
            return period

periodicity = periodicity_rotation


def cycle_degeneracy(cycle):
    return len(cycle)//periodicity(cycle)


def smallest_rotation(lst):
    """Return the lexicographically smallest rotation of a list."""
    lst = list(lst)
    minrot = deque(lst)
    cycle = deque(lst)
    for I in range(len(lst)-1):
        cycle.rotate()
        if list(minrot) > list(cycle):
            minrot = list(deque(cycle))
    return list(minrot)


class RotationTests(unittest.TestCase):
    periods = []
    lists = []

    N = 20
    for n in range(1, N+1):
        for d in divisors(n):
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
