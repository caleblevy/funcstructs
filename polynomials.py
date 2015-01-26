#!/usr/bin/env python
# Copyright (C) 2014-2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.

""" Enumerate and produce polynomials of various kinds. """


from functools import reduce
import numpy as np
import unittest

from multiset import split_set, nCk
import productrange


# MSP == Monomial Symmetric Polynomial
def msp_recursive(x, powers):
    # Wrapper for _recursive_monomial_alg which separates the multiset powers
    # into elements with degeneracies, and returns the value of the function.
    y, d = split_set(powers)
    return _recursive_monomial_alg(x, d, y)


def _recursive_monomial_alg(x, d, y):
    """_recursive_monomial_alg(x, d, y)

    Recursive version of the general formula for evaluating symmetric
    monomial polynomials. This one, while inefficient, is certainly in some
    sense elegant, and is written as such for that reason.

    This function itero-recursive and HIGHLY inefficient, duplicating an
    extraordinary amount of work. It exists as a showcase of the concepts
    behind MSP_iterative. Its running time might be something like
    len(y)^len(x), but either way, do not run this thing with input vectors of
    length greater than about 5 to 10, depending on your system.

    X = (a1,a2,...,an) - Vector of values for polynomial evaluation
    D = (d1,d2,...,dl) - Vector of degeneracies of exponent partitions
    Y = (y1,y2,...,yl) - Vector of exponents

    Premise of formula is given by:
       T(n,d1,...,dl) = T(n-1,d1,...,dl) + an^y1*T(n-1,d1-1,...,dl) + ...
                           ... + an^yl*T(n-1,d1,...,dl-1).

    D and Y need to be of same length.
    """
    # This is the matlab copy version
    if any(I < 0 for I in d):
        return 0
    elif not x:
        if all(I == 0 for I in d):
            return 1
        else:
            return 0
    else:
        val = _recursive_monomial_alg(x[:-1], d, y)
        for I in range(len(d)):
            d_temp = d[:]
            d_temp[I] -= 1
            val += x[-1]**y[I]*_recursive_monomial_alg(x[:-1], d_temp, y)

        return val


def msp_iterative(x, powers):
    """
    Symmetric monomial polynomial formed from the vector x=[x_1,...,x_n] formed
    from the partition of powers partition=[p_1,...,p_l]. It is equivalent to
    the sum (x[a[1]]**p_1)*(x[a[2]]**p_2)*...*(x[a[I]]**p_l) over all a such
    that a[I] != a[J] for 0<=I<J<=l-1 which are not equivalent under
    permutation (I think anyway...).

    If there are distinct powers p_1,...,p_j with multiplicities m_1,...,m_j
    and the list x has n elements then the algorithm runs in O(n*m_1*...*m_j)
    steps, and takes O(m_1*...*m_j) memory in the form of an array of just as
    many dimensions. Inputs may be symbolic, or anything you like.
    """
    n = len(x)
    y, d = split_set(powers)
    l = len(y)
    shape = tuple(I+2 for I in d)

    # Contains 1, possibly 2 more dimensions than necessary.
    T = np.ndarray(shape, object)
    T[:] = 0
    T[(1,)*l] = 1

    # The powers use up sum(multiplcities) of the original x.
    for K in range(n-sum(d)+1):
        for ind in productrange.product_range(1, shape):
            fac = x[K+sum(ind)-l-1]
            for J in range(l):
                ind_prev = list(ind)
                ind_prev[J] -= 1
                T[ind] += fac**y[J]*T[tuple(ind_prev)]

    return T[tuple(I-1 for I in shape)]


def poly_multiply(coeffs1, coeffs2):
    """
    Given numerical lists c and d of length n and m, returns the coefficients
    of P(X)*Q(X) in decreasing order, where
        P(X) = c[-1] + c[-2]*X + ... + c[0]*x^n
        Q(X) = d[-1] + d[-2]*X + ... + d[0]*x^m

    For some reason sympy and numpy do not seem to have this capacity easily
    accessible, or at least nothing dedicated to the purpose. Very likely to be
    faster than the expand method.

    Source taken from:
        "How can I multiply two polynomials in Python using a loop and by
        calling another function?" at http://stackoverflow.com/a/18116401.
    """
    final_coeffs = [0] * (len(coeffs1)+len(coeffs2)-1)
    for ind1, coef1 in enumerate(coeffs1):
        for ind2, coef2 in enumerate(coeffs2):
            final_coeffs[ind1 + ind2] += coef1 * coef2
    return final_coeffs


def FOIL(roots):
    """First Outer Inner Last

    Given a list of values roots, return the polynomial of degree len(roots)+1
    with leading coefficient 1 given by
        (X - roots[0]) * (X - roots[1]) * ... * (X - roots[-1])
    """
    monomials = [(1, -root) for root in roots]
    return reduce(poly_multiply, monomials, [1])


class PolynomialTest(unittest.TestCase):

    def testFOIL(self):
        N = 20
        """Check binomial coefficients."""
        for n in range(N+1):
            binomial_coeffs = [nCk(n, k) for k in range(n+1)]
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


if __name__ == '__main__':
    unittest.main()
