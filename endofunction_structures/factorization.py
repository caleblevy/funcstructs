#!/usr/bin/env python
# Copyright (C) 2014-2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.

""" A collection of short functions for enumerating factorizations of integers
and other such things. """


import fractions

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

prime_divisors = lambda n: list(set(prime_factorization(n)))


def divisorGen(n):
    """
    Find every divisor of an integer n. Code inspired by
        "What is the best way to get all the divisors of a number" at
        http://stackoverflow.com/a/171784.
    """
    factors, powers = multiset.Multiset(prime_factorization(n)).split()
    # Since the factors are prime, every unique partition of powers represents
    # a different divisor.
    for power_combo in productrange.productrange([m+1 for m in powers]):
        yield multiset.prod([factors[I]**p for I, p in enumerate(power_combo)])


divisor_list = lambda n: list(divisorGen(n))


def divisors_memoized(n, factors={}):
    if n not in factors:
        factors[n] = divisor_list(n)
    return factors[n]

divisors = divisors_memoized


def divisor_sum(n, power=1):
    return sum(map(lambda x: pow(x, power), divisors(n)))


def ceildiv(a, b):
    """Does long integer division taking the ceiling instead of the floor"""
    return -(-a // b)


def isdivisor(d, n):
    if ceildiv(n, d) == n//d:
        return True
    return False


def phi_product(n):
    """Return the totient using the fancy prime formula."""
    return int(n*multiset.prod(
        (1-fractions.Fraction(1, p) for p in prime_divisors(n))
    ))


def phi_sum(n):
    """ Return the totient using its definition. Code taken directly from
        "Computing Eulers Totient Function" at
        http://stackoverflow.com/a/18114286
    """
    phi = 0
    for k in range(1, n+1):
        if fractions.gcd(n, k) == 1:
            phi += 1
    return int(phi)

totient = phi_sum
