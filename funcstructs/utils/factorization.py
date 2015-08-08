"""Computation of prime factorizations and divisors.

Caleb Levy, 2014 and 2015.
"""

# Opt to use Counter instead of Multiset to avoid circular dependencies
from collections import Counter

from funcstructs.utils.combinat import prod
from funcstructs.utils.productrange import productrange


__all__ = ["prime_factorization", "divisors"]


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
    return Counter(primfac)


def _divisor_gen(n):
    """Generate divisors of n"""
    # Refactoring of "What is the best way to get all the divisors of a number"
    # at http://stackoverflow.com/a/171784.
    if n == 1:
        yield 1
        return
    primes, multiplicities = zip(*prime_factorization(n).items())
    # Since factors are prime, each partition of powers is a different divisor.
    for exponents in productrange(*[m+1 for m in multiplicities]):
        yield prod(p**e for p, e in zip(primes, exponents))


def divisors(n):
    """Return all integer divisors n."""
    return tuple(_divisor_gen(n))
