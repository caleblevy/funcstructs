import unittest

from ..factorization import prime_factorization, divisors


class FactorizationTests(unittest.TestCase):

    def test_prime_factorization_counts(self):
        """Check number of prime divisors with multiplicity."""
        A001222 = [0, 1, 1, 2, 1, 2, 1, 3, 2, 2, 1, 3, 1, 2, 2, 4, 1, 3, 1, 3,
                   2, 2, 1, 4, 2, 2, 3, 3, 1, 3]
        for i, count in enumerate(A001222, start=1):
            self.assertEqual(count, len(prime_factorization(i)))

    def test_divisor_count(self):
        """Check number of divisors."""
        A000005 = [1, 2, 2, 3, 2, 4, 2, 4, 3, 4, 2, 6, 2, 4, 4, 5, 2, 6, 2, 6,
                   4, 4, 2, 8, 3, 4, 4, 6, 2, 8]
        for i, count in enumerate(A000005, start=1):
            self.assertEqual(count, len(divisors(i)))
