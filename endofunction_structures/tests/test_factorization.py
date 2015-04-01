# Copyright (C) 2014-2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.

import unittest
import math

from endofunction_structures.factorization import *


class FactorizationTests(unittest.TestCase):

    def test_prime_factorization_counts(self):
        """Check number of prime divisors with multiplicity."""
        A001222 = [0, 1, 1, 2, 1, 2, 1, 3, 2, 2, 1, 3, 1, 2, 2, 4, 1, 3, 1, 3,
                   2, 2, 1, 4, 2, 2, 3, 3, 1, 3]
        for i, count in enumerate(A001222, start=1):
            self.assertEqual(count, len(prime_factorization(i)))

    def test_prime_divisor_counts(self):
        """Check number of prime divisors without multiplicity."""
        A001221 = [0, 1, 1, 1, 1, 2, 1, 1, 1, 2, 1, 2, 1, 2, 2, 1, 1, 2, 1, 2,
                   2, 2, 1, 2, 1, 2, 1, 2, 1, 3]
        for i, count in enumerate(A001221, start=1):
            self.assertEqual(count, len(prime_divisors(i)))

    def test_divisor_count(self):
        """Check number of divisors."""
        A000005 = [1, 2, 2, 3, 2, 4, 2, 4, 3, 4, 2, 6, 2, 4, 4, 5, 2, 6, 2, 6,
                   4, 4, 2, 8, 3, 4, 4, 6, 2, 8]
        for i, count in enumerate(A000005, start=1):
            self.assertEqual(count, len(divisors(i)))
            self.assertEqual(count, len(divisors(i)))

    def test_ceildiv(self):
        N = 20
        divrange = list(range(-N, 0))+list(range(1, N+1))
        for i in divrange:
            for j in divrange:
                self.assertEqual(ceildiv(i, j), math.ceil(1.*i/j))

    def test_isdivisor(self):
        for i in range(1, 20):
            for j in range(1, 20):
                self.assertEqual(j in divisors(i), isdivisor(j, i))

    def test_totient(self):
        """OEIS A000010: number of relatively prime smaller integers."""
        values = [1, 1, 2, 2, 4, 2, 6, 4, 6, 4, 10, 4, 12, 6, 8, 8, 16, 6, 18,
                  8, 12, 10, 22, 8, 20, 12, 18]
        for i, val in enumerate(values, start=1):
            self.assertEqual(val, totient(i))
