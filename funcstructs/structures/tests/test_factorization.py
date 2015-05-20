import unittest

from funcstructs import utils
from ..factorization import prime_factorization, divisors


class FactorizationTests(unittest.TestCase):

    def test_prime_factorization_counts(self):
        """Check number of prime divisors with multiplicity."""
        for n in range(1, 30):
            self.assertEqual(n, utils.prod(prime_factorization(n).elements()))

    def test_divisor_count(self):
        """Check number of divisors."""
        A000005 = [1, 2, 2, 3, 2, 4, 2, 4, 3, 4, 2, 6, 2, 4, 4, 5, 2, 6, 2, 6,
                   4, 4, 2, 8, 3, 4, 4, 6, 2, 8]
        for i, count in enumerate(A000005, start=1):
            self.assertEqual(count, len(divisors(i)))
