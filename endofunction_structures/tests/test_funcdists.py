# Copyright (C) 2013, 2014 and 2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.

import unittest

import numpy as np

from endofunction_structures import counts

from endofunction_structures.funcdists import (
    iterdist_brute,
    iterdist_funcstruct, iterdist,
    imagedist_composition, imagedist_recurse,
    nCk_grid,
    powergrid,
    limitdist_composition, limitdist_direct, limitdist_recurse
)


class EndofunctionTest(unittest.TestCase):

    def test_iterdist(self):
        """Check the multiplicities of sizes of images of iterates."""
        iterdists = [
            np.array([
                [3, 9],
                [18, 12],
                [6, 6]], dtype=object),
            np.array([
                [4, 40, 64],
                [84, 120, 96],
                [144, 72, 72],
                [24, 24, 24]], dtype=object),
            np.array([
                [5, 205, 505, 625],
                [300, 1060, 1120, 1000],
                [1500, 1260, 900, 900],
                [1200, 480, 480, 480],
                [120, 120, 120, 120]], dtype=object)
        ]
        for dist in iterdists:
            n = dist.shape[0]
            np.testing.assert_array_equal(dist, iterdist_brute(n))
            np.testing.assert_array_equal(dist, iterdist_funcstruct(n))

    def test_rootedtree_funcs(self):
        """ Test iterdist(n)[k] == labelled rooted trees of height at most k on
        n nodes. Corresponds to the top row of imagedist. """
        # Distribution of functions whose nth iterate has size 1
        A236396 = [
            [3, 9],
            [4, 40, 64],
            [5, 205, 505, 625],
            [6, 1176, 4536, 7056, 7776],
            [7, 7399, 46249, 89929, 112609, 117649],
            [8, 50576, 526352, 1284032, 1835072, 2056832, 2097152]
        ]
        for dist in A236396:
            n = len(dist) + 1
            self.assertSequenceEqual(dist, list(iterdist_funcstruct(n)[0, :]))

    def test_imagedists(self):
        """ Test imagedist(n)[h] = number of functions in
        TransformationMonoid(n) such that |Image(f)|=h for h in {1, 2, ..., n}.
        """
        A101817 = [
            [2, 2],
            [3, 18, 6],
            [4, 84, 144, 24],
            [5, 300, 1500, 1200, 120],
            [6, 930, 10800, 23400, 10800, 720],
            [7, 2646, 63210, 294000, 352800, 105840, 5040]
        ]
        for dist in A101817:
            n = len(dist)
            self.assertSequenceEqual(dist, list(iterdist(n)[:, 0]))
            self.assertSequenceEqual(dist, imagedist_composition(n))
            self.assertSequenceEqual(dist, imagedist_recurse(n))

    def test_binomial_grid(self):
        """Check that nCk(n,k) == nCk_table[n,k] for 0 <= k <= n <= N"""
        N = 20
        binomial_coeffs = nCk_grid(N)
        for n in range(N+1):
            for k in range(n+1):
                self.assertEqual(counts.nCk(n, k), binomial_coeffs[n, k])

    def test_power_grid(self):
        """I**J == powergrid[I,J] for 0 <= I, J <= N. Note 0^0 defined as 1."""
        N = 20
        exponentials = powergrid(N)
        for I in range(N+1):
            for J in range(N+1):
                if I == J == 0:
                    self.assertEqual(1, exponentials[I, J])
                else:
                    self.assertEqual(I**J, exponentials[I, J])

    def test_limitdists(self):
        """ Test limitdist(n)[k] == number of endofunctions on n labeled points
        constructed from k rooted trees. """
        A066324 = [
            [2, 2],
            [9, 12, 6],
            [64, 96, 72, 24],
            [625, 1000, 900, 480, 120],
            [7776, 12960, 12960, 8640, 3600, 720],
            [117649, 201684, 216090, 164640, 88200, 30240, 5040]
        ]
        for dist in A066324:
            n = len(dist)
            self.assertSequenceEqual(dist, list(iterdist(n)[:, -1]))
            self.assertSequenceEqual(dist, limitdist_composition(n))
            self.assertSequenceEqual(dist, limitdist_direct(n))
            self.assertSequenceEqual(dist, limitdist_recurse(n))
