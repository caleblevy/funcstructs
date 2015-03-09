# Copyright (C) 2014-2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.

""" Computation of prime factorizations and divisors. """

import fractions

from . import counts
from . import multiset
from . import productrange


def prime_factorization(n):
    """
    Find the prime factorization of an integer n. Code taken directly from
        "Prime factorization - list" at http://stackoverflow.com/a/16996439.
    """
    primfac = []
    d = 2
    while d*d <= n:
        while (n % d) == 0:
            primfac.append(d)  # supposing you want multiple factors repeated
            n //= d
        d += 1
    if n > 1:
        primfac.append(n)
    return primfac


def prime_divisors(n):
    return list(set(prime_factorization(n)))


def _divisor_gen(n):
    """
    Find every divisor of an integer n. Code inspired by
        "What is the best way to get all the divisors of a number" at
        http://stackoverflow.com/a/171784.
    """
    factors, powers = multiset.Multiset(prime_factorization(n)).split()
    # Since the factors are prime, every unique partition of powers represents
    # a different divisor.
    for power_combo in productrange.productrange([m+1 for m in powers]):
        yield counts.prod([factors[i]**p for i, p in enumerate(power_combo)])


def divisors(n, factors={}):
    if n not in factors:
        factors[n] = list(_divisor_gen(n))
    return factors[n]


def ceildiv(a, b):
    """Does long integer division taking the ceiling instead of the floor"""
    return -(-a // b)


def isdivisor(d, n):
    return ceildiv(n, d) == n//d


def totient(n):
    """Return the totient using the fancy prime formula."""
    return int(n*counts.prod(
        (1-fractions.Fraction(1, p) for p in prime_divisors(n))
    ))
