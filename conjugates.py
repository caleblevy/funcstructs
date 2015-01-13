#!/usr/bin/env python
# Copyright (C) 2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.

"""
These should all be made into methods. We will have:
    - f.cycles()
    - f.preimage(I)
"""

from random import randrange
from collections import deque

from funcdists import endofunctions, imagepath
from nestops import flatten

import unittest

randfunc = lambda n: [randrange(n) for I in range(n)]


def funccycles(f):
    """
    Given an endofunction f, return its cycle decomposition.
    """
    N = len(f)
    if N == 1:
        return [(0, ), ]
    cycles = []
    cycle_els = []
    if N == 1:
        return [(0, ), ]
    for x in range(N):
        path = [x]
        for it in range(N):
            x = f[x]
            path.append(x)
        I = N-1
        while I >= 0 and path[I] != path[-1]:
            I -= 1
        if path[-1] not in cycle_els:
            cycles.append(tuple(path[I+1:]))
            cycle_els.extend(path[I+1:])
    return cycles


def smallest_rotation(lst):
    """Find the lexicographically smallest rotation of a list lst."""
    lst = list(lst)
    minrot = deque(lst)
    cycle = deque(lst)
    for I in range(len(lst)-1):
        cycle.rotate()
        cy = list(cycle)
        if minrot > cy:
            minrot = cy
    return tuple(minrot)


class CycleTests(unittest.TestCase):
    funcs = [
        [1, 0],
        [9, 5, 7, 6, 2, 0, 9, 5, 7, 6, 2],
        [7, 2, 2, 3, 4, 3, 9, 2, 2, 10, 10, 11, 12, 5]
    ]
    # Use magic number for python3 compatibility
    funcs += list([randfunc(20) for I in range(100)])
    funcs += list(endofunctions(1))
    funcs += list(endofunctions(3)) + list(endofunctions(4))

    def testCyclesAreCyclic(self):
        for f in self.funcs:
            c = funccycles(f)
            for cycle in c:
                for ind, el in enumerate(cycle):
                    self.assertEqual(cycle[(ind+1) % len(cycle)], f[el])

    def testCyclesAreUnique(self):
        for f in self.funcs:
            cycle_els = list(flatten(funccycles(f)))
            self.assertEqual(len(cycle_els), len(set(cycle_els)))

    def testCyclesAreComplete(self):
        for f in self.funcs:
            cycle_size = len(flatten(funccycles(f)))
            self.assertEqual(imagepath(f)[-1], cycle_size)


if __name__ == '__main__':
    unittest.main()
