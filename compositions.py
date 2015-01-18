#!/usr/bin/env python
# Copyright (C) 2014-2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.


"""
A composition of an integer N is an ordered tuple of positive integers which
sum to N, for example:

    4 = 4
      = 3 + 1
      = 2 + 2
      = 2 + 1 + 1
      = 1 + 3
      = 1 + 2 + 1
      = 1 + 1 + 2
      = 1 + 1 + 1 +1

The compositions of 4 are thus (4), (3,1), (2,2), (2,1,1), (1,3), (1,2,1),
(1,1,2) and (1,1,1,1).

One can see a clear correspondance between compositions of N and the subsets of
a set with N-1 elements. Simply list N zeros in a row; every way to draw
dividing lines between the zeros is a different composition. These correspond
to binary digits of numbers of length up to N-1. There are thus 2^(N-1)
compositions of N.
"""


import unittest
import productrange


def compositions_binary(n):
    """Additive compositions of a number; i.e. partitions with ordering."""
    for binary_composition in productrange.product_range([2]*(n-1)):
        tot = 1
        composition = []
        for I in binary_composition:
            if I:
                composition.append(tot)
                tot = 1
                continue
            tot += 1
        composition.append(tot)
        yield composition


def compositions_simple(n):
    """A more direct way of enumerating compositions."""
    comp = [n]
    while True:
        yield comp
        J = len(comp)
        if J == n:
            return
        for K in range(J-1, -1, -1):
            # Keep descending (backwards) until hitting a "step" you can
            # subtract from
            if comp[K] is not 1:
                comp[K] -= 1
                comp.append(J-K)
                break
            # Haven't hit the target, pop the last element, and step back
            comp.pop()

compositions = compositions_simple  # best by test.


class CompositionTest(unittest.TestCase):

    def testCompositionCounts(self):
        N = 10
        for n in range(1, N):
            self.assertEqual(2**(n-1), len(list(compositions_simple(n))))
            self.assertEqual(2**(n-1), len(list(compositions_binary(n))))

    def testCompositionSums(self):
        N = 10
        for n in range(1, N):
            for comp in compositions_simple(n):
                self.assertEqual(n, sum(comp))
            for comp in compositions_binary(n):
                self.assertEqual(n, sum(comp))


if __name__ == '__main__':
    unittest.main()
