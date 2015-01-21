#!/usr/bin/env python
# Copyright (C) 2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.


"""
Functions for conjugating endofunctions.
"""

import random
import unittest

import iterate
import productrange


def randperm(n):
    """Returns a random permutation of range(n)."""
    r = list(range(n))  # Explicitly call ist for python 3 compatibility.
    random.shuffle(r)
    return r


def inv(perm):
    """
    Returns the inverse of a permutation of range(n). Code taken directly from:
      "Inverting permutations in Python" at http://stackoverflow.com/a/9185908.
    """
    inverse = [0] * len(perm)
    for i, p in enumerate(perm):
        inverse[p] = i
    return inverse


def conjugate(perm, f):
    """Conjugate a function f by a permutation."""
    return iterate.compose(inv(perm), iterate.compose(f, perm))


def randconj(f):
    """Return a random conjugate of f."""
    r = randperm(len(f))
    return conjugate(r, f)


class PermutationTests(unittest.TestCase):

    def testInversePermutations(self):
        """Test compose(inv(perm), perm) == perm"""
        permlist = []
        for n in range(1, 10):
            for _ in range(1, 10*n):
                permlist.append(randperm(n))

        for perm in permlist:
            identity = list(range(len(perm)))
            self.assertEqual(identity, iterate.compose(perm, inv(perm)))
            self.assertEqual(identity, iterate.compose(inv(perm), perm))

    def testConjugation(self):
        """Test that conjugation is invertible, with the obvious inverse."""
        funclist = list(productrange.endofunctions(4))
        funclist += [iterate.randfunc(20) for _ in range(100)]
        funclist += list(productrange.endofunctions(2))
        for f in funclist:
            for _ in range(20):
                perm = randperm(len(f))
                iperm = inv(perm)
                self.assertEqual(list(f), conjugate(iperm, conjugate(perm, f)))


if __name__ == '__main__':
    unittest.main()
