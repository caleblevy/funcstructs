#!/usr/bin/env python
# Copyright (C) 2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.

import unittest

from endofunction_structures.polynomials import *


class PolynomialTests(unittest.TestCase):

    def test_foil(self):
        """Check binomial coefficients."""
        for n in range(20):
            binomial_coeffs = [multiset.nCk(n, k) for k in range(n+1)]
            self.assertSequenceEqual(binomial_coeffs, FOIL([-1]*n))

    def test_monomial_symmetric_polynomial(self):
        """
        Verify MSP for the simple case of the elementary symmetric polynomials.
        We can calculate them independently by using the Newton identities to
        FOIL a polynomial with the given roots.
        """
        for n in range(1, 20):
            foilmon = FOIL(range(-n, 0))[1:]
            x = range(1, n+1)
            symmon = [
                monomial_symmetric_polynomial(x, [1]*I) for I in range(1, n+1)
            ]
            self.assertSequenceEqual(foilmon, symmon)

        vecs = [[5, 5, 5], [1, 2, 3, 4, 5, 6, 7, 8]]
        powers = [[3, 3, 2], [4, 4, 3, 3, 2]]
        counts = [1171875, 139100509734480]
        for vec, power, count in zip(vecs, powers, counts):
            self.assertEqual(count, monomial_symmetric_polynomial(vec, power))
