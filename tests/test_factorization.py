#!/usr/bin/env python
# Copyright (C) 2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.

import unittest
import math

from endofunction_structures.factorization import *


class FactorizationTests(unittest.TestCase):

    def test_prime_factorization_counts(self):
        """OEIS A001222: number of prime divisors with multiplicity."""
        counts = [0, 1, 1, 2, 1, 2, 1, 3, 2, 2, 1, 3, 1, 2, 2, 4, 1, 3, 1, 3,
                  2, 2, 1, 4, 2, 2, 3, 3, 1, 3]
        for I in range(1, len(counts)+1):
            self.assertEqual(counts[I-1], len(prime_factorization(I)))

    def test_prime_divisor_counts(self):
        """OEIS A001221: number of prime divisors without multiplicity."""
        counts = [0, 1, 1, 1, 1, 2, 1, 1, 1, 2, 1, 2, 1, 2, 2, 1, 1, 2, 1, 2,
                  2, 2, 1, 2, 1, 2, 1, 2, 1, 3]
        for I in range(1, len(counts)+1):
            self.assertEqual(counts[I-1], len(prime_divisors(I)))

    def test_divisor_count(self):
        """OEIS A000005: number of divisors."""
        A000005 = [1, 2, 2, 3, 2, 4, 2, 4, 3, 4, 2, 6, 2, 4, 4, 5, 2, 6, 2, 6,
                   4, 4, 2, 8, 3, 4, 4, 6, 2, 8]
        for I, divcount in enumerate(A000005):
            self.assertEqual(divcount, len(divisors(I+1)))
            self.assertEqual(divcount, len(divisors(I+1)))

    def test_ceildiv(self):
        N = 20
        divrange = list(range(-N, 0))+list(range(1, N+1))
        for I in divrange:
            for J in divrange:
                self.assertEqual(ceildiv(I, J), math.ceil(1.*I/J))

    def test_isdivisor(self):
        N = 20
        for I in range(1, N):
            for J in range(1, N):
                self.assertEqual(J in divisors(I), isdivisor(J, I))

    def test_divisor_sums(self):
        """Test sums of powers of divisors. Features:
            -OEIS A000005: divisor_sum(n,0)
            -OEIS A000203: divisor_sum(n,1)
            -OEIS A001157: divisor_sum(n,2)
            -OEIS A001158: divisor_sum(n,3)
        """
        sums = [
            [1, 2, 2, 3, 2, 4, 2, 4, 3, 4, 2, 6],
            [1, 3, 4, 7, 6, 12, 8, 15, 13, 18],
            [1, 5, 10, 21, 26, 50, 50, 85, 91, 130],
            [1, 9, 28, 73, 126, 252, 344, 585, 757, 1134]
        ]
        for power, seq in enumerate(sums):
            for n, tot in enumerate(seq):
                self.assertEqual(tot, divisor_sum(n+1, power))

    def test_Euler_totient(self):
        """OEIS A000010: number of relatively prime smaller integers."""
        values = [1, 1, 2, 2, 4, 2, 6, 4, 6, 4, 10, 4, 12, 6, 8, 8, 16, 6, 18,
                  8, 12, 10, 22, 8, 20, 12, 18]
        for I in range(1, len(values)+1):
            self.assertEqual(values[I-1], phi_product(I))
            self.assertEqual(values[I-1], phi_sum(I))
