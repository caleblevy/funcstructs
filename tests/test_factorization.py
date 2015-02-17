import unittest
from endofunction_structures.factorization import *

class FactorizationTests(unittest.TestCase):

    def testPrimeDivisorsRepeated(self):
        """OEIS A001222: number of prime divisors with multiplicity."""
        counts = [0, 1, 1, 2, 1, 2, 1, 3, 2, 2, 1, 3, 1, 2, 2, 4, 1, 3, 1, 3,
                  2, 2, 1, 4, 2, 2, 3, 3, 1, 3]
        for I in range(1, len(counts)+1):
            self.assertEqual(counts[I-1], len(prime_factorization(I)))

    def testPrimeDivisorsNonrepeated(self):
        """OEIS A001221: number of prime divisors without multiplicity."""
        counts = [0, 1, 1, 1, 1, 2, 1, 1, 1, 2, 1, 2, 1, 2, 2, 1, 1, 2, 1, 2,
                  2, 2, 1, 2, 1, 2, 1, 2, 1, 3]
        for I in range(1, len(counts)+1):
            self.assertEqual(counts[I-1], len(prime_divisors(I)))

    def testDivisorCount(self):
        """OEIS A000005: number of divisors."""
        A000005 = [1, 2, 2, 3, 2, 4, 2, 4, 3, 4, 2, 6, 2, 4, 4, 5, 2, 6, 2, 6,
                   4, 4, 2, 8, 3, 4, 4, 6, 2, 8]
        for I, divcount in enumerate(A000005):
            self.assertEqual(divcount, len(divisors(I+1)))
            self.assertEqual(divcount, len(divisors(I+1)))

    def testCeildiv(self):
        N = 20
        divrange = list(range(-N, 0))+list(range(1, N+1))
        for I in divrange:
            for J in divrange:
                self.assertEqual(ceildiv(I, J), ceil(1.*I/J))

    def testIsDivisor(self):
        N = 20
        for I in range(1, N):
            for J in range(1, N):
                self.assertEqual(J in divisors(I), isdivisor(J, I))

    def testDivisorSigma(self):
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

    def testTotients(self):
        """OEIS A000010: number of relatively prime smaller integers."""
        values = [1, 1, 2, 2, 4, 2, 6, 4, 6, 4, 10, 4, 12, 6, 8, 8, 16, 6, 18,
                  8, 12, 10, 22, 8, 20, 12, 18]
        for I in range(1, len(values)+1):
            self.assertEqual(values[I-1], phi_product(I))
            self.assertEqual(values[I-1], phi_sum(I))