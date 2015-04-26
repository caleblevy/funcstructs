import unittest

from endofunction_structures import counts, multiset

from endofunction_structures.polynomials import (
    monomial_symmetric_polynomial,
    FOIL,
    MultisetPolynomial,
    multisets_with_multiplicities
)


class PolynomialTests(unittest.TestCase):

    def test_foil(self):
        """Check binomial coefficients."""
        for n in range(20):
            binomial_coeffs = [counts.nCk(n, k) for k in range(n+1)]
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
        vals = [1171875, 139100509734480]
        for vec, power, val in zip(vecs, powers, vals):
            self.assertEqual(val, monomial_symmetric_polynomial(vec, power))


class MultisetPolynomialTests(unittest.TestCase):

    def test_init(self):
        self.assertEqual(MultisetPolynomial(1), MultisetPolynomial([1]))
        self.assertEqual(MultisetPolynomial(1), MultisetPolynomial([[1]]))
        self.assertEqual(
            MultisetPolynomial(1),
            MultisetPolynomial(MultisetPolynomial(1))
        )
        self.assertEqual(
            MultisetPolynomial([1, 2]),
            MultisetPolynomial([[1], [2]])
        )
        self.assertEqual(
            MultisetPolynomial([1, 2]),
            MultisetPolynomial([[1], 2])
        )
        self.assertEqual(
            MultisetPolynomial([2, 1]),
            MultisetPolynomial([1, 2])
        )

    def test_repr(self):
        a = MultisetPolynomial([[1, 2, 3, 3], [1, 2, 3, 3], [1, 2]])
        self.assertEqual(a, eval(repr(a), globals(), {
            'Multiset': multiset.Multiset
        }))

    def test_addition(self):
        """Test the addition obeys ring properties"""
        self.assertEqual(
            MultisetPolynomial([1, 2, 2, 3]),
            MultisetPolynomial([1, 2]) + MultisetPolynomial([2, 3])
        )
        # Ensure the addition is abelian
        a = MultisetPolynomial([1, 2])
        b = MultisetPolynomial([3, 4])
        c = MultisetPolynomial([5, [6, 7]])
        self.assertEqual(a+b+c, c+a+b)
        # Test that zero is additive identity
        self.assertEqual(
            MultisetPolynomial([1, 2]),
            MultisetPolynomial([1, 2]) + 0
        )
        self.assertEqual(
            MultisetPolynomial([1, 2]) + 0,
            0 + MultisetPolynomial([1, 2])
        )

    def test_multiplication(self):
        """Test that the multiplication is well defined"""
        self.assertEqual(
            MultisetPolynomial([1, 2]) * MultisetPolynomial([3, 4]),
            MultisetPolynomial([[1, 3], [1, 4], [2, 3], [2, 4]])
        )
        # Test multiplicative identity
        self.assertEqual(MultisetPolynomial(1), MultisetPolynomial(1) * 1)
        self.assertEqual(MultisetPolynomial(1), 1 * MultisetPolynomial([1]))
        # Test 0
        self.assertEqual(0, 0*MultisetPolynomial([1]))
        self.assertEqual(0, MultisetPolynomial([1])*0)
        # Test the multiplication is commutative
        a = MultisetPolynomial([1, 1, 2])
        b = MultisetPolynomial([1, [1, 2]])
        c = MultisetPolynomial([1, 2, 3])
        self.assertEqual(a*b, b*a)
        self.assertEqual(a*c, c*a)
        self.assertEqual(b*c, c*b)

    def test_pow(self):
        self.assertEqual(
            MultisetPolynomial([[1, 1], [2, 2]]) ** 3,
            MultisetPolynomial([
                [1, 1, 1, 1],
                [2, 2, 2, 2],
                [1, 1, 2, 2],
                [2, 2, 1, 1]
            ]) * MultisetPolynomial([[1, 1], [2, 2]])
        )
        a = MultisetPolynomial([[1, 1, 2], [3, 3, 4], [5], 5])
        self.assertEqual(a*a*a*a, a**4)

    def test_distributivity(self):
        """Test the multiplication is left and right distributive"""
        a = MultisetPolynomial([1, 1, 2])
        b = MultisetPolynomial([1, 2])
        c = MultisetPolynomial([3, 4])
        self.assertEqual(a*(b+c), a*b + a*c)
        self.assertEqual((a+b)*c, a*c + b*c)

    def test_msp(self):
        """ Ensure MultisetPolynomial satisfies the requirements of a symmetric
        monomial polynomial. """
        self.assertEqual(
            MultisetPolynomial(
                multisets_with_multiplicities([2, 3, 14], [2, 2])
            ),
            MultisetPolynomial([[2, 2, 3, 3], [2, 2, 14, 14], [3, 3, 14, 14]])
        )
