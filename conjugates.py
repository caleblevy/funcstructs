#!/usr/bin/env python
# Copyright (C) 2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.


"""
A collection of utilities returning certain information about and kinds of
images of sets under functions: preimages, cardinalities of iterate images,
cycle decompositions and limitsets.

"""

import random
import unittest


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


class PermutationTests(unittest.TestCase):

    def testInversePermutations(self):
        """Test compose(inv(perm), perm) == perm"""
        import iterate

        permlist = []
        for n in range(1, 10):
            for _ in range(1, 10*n):
                permlist.append(randperm(n))

        for perm in permlist:
            identity = list(range(len(perm)))
            self.assertEqual(identity, iterate.compose(perm, inv(perm)))
            self.assertEqual(identity, iterate.compose(inv(perm), perm))


if __name__ == '__main__':
    unittest.main()
