import unittest

from funcstructs.combinat import (
    nCk, prod, compositions, weak_compositions, prime_factorization, divisors
)


class CompositionTests(unittest.TestCase):

    def test_composition_counts(self):
        """Ensure #(compositions(n)) = 2^(n-1)"""
        n = 10
        for i in range(1, n):
            self.assertEqual(2**(i-1), len(list(compositions(i))))

    def test_composition_sums(self):
        """Check that compositions of n sum to n"""
        n = 10
        for i in range(1, n):
            for comp in compositions(i):
                self.assertEqual(i, sum(comp))

    def test_weak_composition_counts(self):
        """Ensure there are nCk(n, k) weak compositions of n into k parts."""
        for n in range(1, 5):
            for k in range(1, 10):
                self.assertEqual(
                    nCk(n+k-1, k-1),
                    len(list(weak_compositions(n, k)))
                )

    def test_weak_composition_sums(self):
        """Ensure each weak composition sums to n"""
        for n in range(1, 5):
            for k in range(1, 10):
                for comp in weak_compositions(n, k):
                    self.assertEqual(n, sum(comp))


class FactorizationTests(unittest.TestCase):

    def test_prime_factorization_counts(self):
        """Check number of prime divisors with multiplicity."""
        for n in range(1, 30):
            self.assertEqual(n, prod(prime_factorization(n)))

    def test_divisor_count(self):
        """Check number of divisors."""
        A000005 = [1, 2, 2, 3, 2, 4, 2, 4, 3, 4, 2, 6, 2, 4, 4, 5, 2, 6, 2, 6,
                   4, 4, 2, 8, 3, 4, 4, 6, 2, 8]
        for i, count in enumerate(A000005, start=1):
            self.assertEqual(count, len(divisors(i)))
