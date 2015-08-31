"""Collection of functions for basic combinatorial counting.

Caleb Levy, 2015.
"""

from math import factorial
from itertools import product

from funcstructs.utils import split
from funcstructs.structures.multiset import (
    Multiset,
    _prod as prod,
    _factorial_prod as factorial_prod
)


def nCk(n, k):
    """n choose k == n!/k!/(n-k)!, optimized for large n and small k"""
    return factorial(n)//factorial(k)//factorial(n-k)


def multinomial_coefficient(partition, n=None):
    """The multinomial coefficient of n corresponding to partition [p1, ...,
    pk] is given by n!/(p1! *...* pk!)/(n-sum(partition))!"""
    tot = 0
    deg = 1
    for p in partition:
        tot += p
        deg *= factorial(p)
    if n is None:
        n = tot
    return factorial(n)//deg//factorial(n-tot)


def nCWRk(n, r):
    """Returns nCk(n+r-1, n-1) optimized for large n and small r."""
    val = 1
    for i in range(1, r+1):
        val *= n + r - i
        val //= i
    return val


# productrange


def productrange(*ranges):
    """Cartesian product of range mapped to each of the ranges. For example,

    productrange(3, 2) --> product(range(3), range(2))
    productrange(5, (2, 10, 3)) --> product(range(5), range(2, 10, 3))
    """
    _ranges = []
    for r in ranges:
        if isinstance(r, int):
            _ranges.append(range(r))
        else:
            _ranges.append(range(*r))
    return product(*_ranges)


# prime factorization


def prime_factorization(n):
    """Prime factorization of an integer n."""
    # Code taken directly from "Prime factorization - list" at
    # http://stackoverflow.com/a/16996439.
    primfac = []
    d = 2
    while d*d <= n:
        while (n % d) == 0:
            primfac.append(d)  # supposing you want multiple factors repeated
            n //= d
        d += 1
    if n > 1:
        primfac.append(n)
    return Multiset(primfac)


def _divisor_gen(n):
    """Generate divisors of n"""
    # Refactoring of "What is the best way to get all the divisors of a number"
    # at http://stackoverflow.com/a/171784.
    if n == 1:
        yield 1
        return
    primes, multiplicities = split(prime_factorization(n))
    # Since factors are prime, each partition of powers is a different divisor.
    for exponents in productrange(*[m+1 for m in multiplicities]):
        yield prod(p**e for p, e in zip(primes, exponents))


def divisors(n):
    """Return all integer divisors n."""
    return tuple(_divisor_gen(n))


# Compositions


def binary_compositions(n):
    """The division marker representation of each composition."""
    return productrange(*[2]*(n-1))


def compositions(n):
    """Enumerate ordered lists of positive integers summing to n."""
    comp = [n]
    while comp:
        yield comp
        j = len(comp)
        for k in range(j-1, -1, -1):
            # Keep descending (backwards) until hitting a component you can
            # subtract from
            if comp[k] > 1:
                comp[k] -= 1
                comp.append(j-k)
                break
            # Haven't hit a 1, pop the last element, and step back
            comp.pop()


def weak_compositions(n, k):
    """Enumerates the length k lists of non-negative integers summing to n.
    Taken directly from http://dandrake.livejournal.com/83095.html."""
    if n < 0 or k < 0:
        return
    elif k == 0:
        # the empty sum, by convention, is zero, so only return something if
        # n is zero
        if n == 0:
            yield []
        return
    elif k == 1:
        yield [n]
        return
    else:
        # For each first integer i in range(n+1), list all compositions
        # on n-i nodes, of length at most k-1.
        for i in range(n+1):
            for comp in weak_compositions(n-i, k-1):
                yield [i] + comp
