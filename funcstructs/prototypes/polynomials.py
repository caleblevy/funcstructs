"""Enumerate and produce polynomials of various kinds.

Caleb Levy, 2014 and 2015.
"""

import collections
from functools import reduce
from itertools import repeat

import numpy as np

from funcstructs.combinat import productrange
from funcstructs.utils import split
from funcstructs.structures.multiset import Multiset


def monomial_symmetric_polynomial(x, powers):
    """ Symmetric monomial polynomial with partition of powers [p_1, ..., p_j]
    evaluated at the vector of values [x_1, ..., x_n]. The partition is further
    split into two vectors:

        (e_1, e_2, ..., e_l) - vector of exponent values;
        (m_1, m_2, ..., m_l) - vector of multiplicities of each exponent

    Instead of summing over all possible monomial terms, we use the recursion
    relation

        T(n, m_1, ..., m_l) =   T(n-1, m_1, ..., m_l)
                              + x_n**e_1 * T(n-1, m_1-1, m_2, ..., m_l)
                              + x_n**e_2 * T(n-1, m_1, m_2-1, ..., m_l)
                              + ...
                              + x_n**e_l * T(n-1, m_1, m_2, ..., m_l-1),

    where T(n, m_1, ..., m_l) is the symmetric monomial polynomial with the
    same powers evaluated with multiplicities (m_1, ..., m_l). This exploits
    additive and multiplicative associativity and commutativity to avoid
    repeated work.

    This algorithm runs in O(n * m_1 *...* m_k) steps, and requires an array of
    size O(m_1 *...* m_j) for storing previous terms of the recurrence. For
    fun, you can input an array of symbolic variables from sympy and get fast
    evaluation of many variable polynomials via a numpy array with object
    elements. """

    n = len(x)
    pows, mults = split(Multiset(powers))
    l = len(pows)
    shape = tuple(i+2 for i in mults)

    # Contains 1, possibly 2 more dimensions than necessary.
    T = np.ndarray(shape, object)
    T[:] = 0
    T[(1, )*l] = 1

    # The powers use up sum(multiplcities) of the original x.
    for k in range(n-sum(mults)+1):
        for ind in productrange(*[(1, s) for s in shape]):
            fac = x[k+sum(ind)-l-1]
            for j in range(l):
                ind_prev = list(ind)
                ind_prev[j] -= 1
                T[ind] += fac**pows[j]*T[tuple(ind_prev)]

    return T[tuple(i-1 for i in shape)]


def FOIL(roots):
    """First Outer Inner Last

    Given a list of values roots, return the polynomial of degree len(roots)+1
    with leading coefficient 1 given by
        (X - roots[0]) * (X - roots[1]) * ... * (X - roots[-1])
    """
    monomials = [(1, -root) for root in roots]
    return tuple(reduce(np.polymul, monomials, np.array([1], dtype=object)))


def newton_elementary_polynomial(x, n):
    """Calculate the nth elementary symmetric polynomial in values x
    using the Newton identities."""
    e = [0]*(n+1)
    p = [sum(map(pow, x, repeat(i))) for i in range(n+1)]
    e[0] = 1
    e[1] = p[1]
    for i in range(2, n+1):
        for j in range(1, i+1):
            e[i] += (-1)**(j-1) * e[i-j]*p[j]
        e[i] /= i
    return e[-1]


def elementary_symmetric_polynomial(x, n):
    """Returns the nth elementary symmetric polynomial in list of values x."""
    return monomial_symmetric_polynomial(x, [1]*n)


class MultisetPolynomial(object):
    """A commutative ring with identity consisting of collections of multisets.
    The addition of elements is defined by their union, and the multiplication
    by union of all pairwise unions of their elements.

    These multiset collections function essentially as multinomials where the
    free variables are the elements of the multisets and the exponents are the
    multiplicities They are built to be fed into a symmetric monomial
    polynomial to be expanded into lists of multisets. """

    def __init__(self, iterable=None):
        self.cpart = collections.Counter()
        if iterable is not None:
            if hasattr(iterable, 'elements'):
                iterable = iterable.elements()
            if hasattr(iterable, '__iter__'):
                for el in iterable:
                    if not hasattr(el, '__iter__'):
                        el = [el]
                    self.cpart.update([Multiset(el)])
            else:
                self.cpart.update([Multiset([iterable])])

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.cpart == other.cpart
        return False

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return self.__class__.__name__+'(%s)' % list(self.cpart.elements())

    def __str__(self):
        set_str = str(Multiset(self.cpart.elements()))[1:-1]
        if not self.cpart:
            set_str = '{}'
        return self.__class__.__name__+'(%s)' % set_str

    def __iter__(self):
        return (el for el in self.cpart.elements())

    def __add__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(self.cpart + other.cpart)
        elif other == 0:
            return self
        raise TypeError(
            "Cannot perform arithmetic with %s and %s" % (
                self.__class__.__name__, other.__class__.__name__
            )
        )

    def __radd__(self, other):
        return self + other

    def __mul__(self, other):
        if isinstance(other, self.__class__):
            lol = []
            for l1 in self:
                for l2 in other:
                    lol.append(list(l1)+list(l2))
            return self.__class__(lol)
        elif other == 1:
            return self
        elif other == 0:
            return 0
        raise TypeError(
            "Cannot perform arithmetic with %s and %s" % (
                self.__class__.__name__, other.__class__.__name__
            )
        )

    def __rmul__(self, other):
        return self * other

    def __pow__(self, n):
        cp = 1
        for _ in range(n):
            cp *= self
        return cp


def multisets_with_multiplicities(elems, multiplicities):
    x = [MultisetPolynomial(el) for el in elems]
    for mset in monomial_symmetric_polynomial(x, multiplicities):
        yield Multiset(mset)
