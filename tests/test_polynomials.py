import unittest
from endofunction_structures.polynomials import *

class PolynomialTests(unittest.TestCase):

    def testFOIL(self):
        N = 20
        """Check binomial coefficients."""
        for n in range(N+1):
            binomial_coeffs = [multiset.nCk(n, k) for k in range(n+1)]
            self.assertSequenceEqual(binomial_coeffs, FOIL([-1]*n))

    def testMonomialSymmetricPolynomial(self):
        """
        Verify MSP for the simple case of the elementary symmetric polynomials.
        We can calculate them independently by using the Newton identities to
        FOIL a polynomial with the given roots.
        """
        N = 20
        for n in range(1, N):
            foilmon = FOIL(range(-n, 0))[1:]
            x = range(1, n+1)
            symmon = [msp_iterative(x, [1]*I) for I in range(1, n+1)]
            self.assertSequenceEqual(foilmon, symmon)
            # Recursive version is far more expensive; test small values.
            if n <= 5:
                recmon = [msp_recursive(x, [1]*I) for I in range(1, n+1)]
                self.assertSequenceEqual(foilmon, recmon)

        vecs = [[5, 5, 5], [1, 2, 3, 4, 5, 6, 7, 8]]
        powers = [[3, 3, 2], [4, 4, 3, 3, 2]]
        counts = [1171875, 139100509734480]
        for vec, power, count in zip(vecs, powers, counts):
            self.assertEqual(count, msp_iterative(vec, power))
            self.assertEqual(count, msp_recursive(vec, power))