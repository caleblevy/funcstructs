"""Computation of prime factorizations and divisors.

Caleb Levy, 2014 and 2015.
"""

from . import counts, multiset, productrange

__all__ = ["prime_factorization", "prime_divisors", "divisors"]


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
    return multiset.Multiset(primfac)


def prime_divisors(n):
    """Return all prime factors of n"""
    return prime_factorization(n).items()


def _divisor_gen(n):
    # Refactoring of "What is the best way to get all the divisors of a number"
    # at http://stackoverflow.com/a/171784.
    primes, multiplicities = multiset.Multiset(prime_factorization(n)).split()
    # Since factors are prime, each partition of powers is a different divisor.
    for exponents in productrange.productrange([m+1 for m in multiplicities]):
        yield counts.prod([p**e for p, e in zip(primes, exponents)])


def divisors(n, factors={}):
    """Return all integer divisors n."""
    if n not in factors:
        factors[n] = tuple(_divisor_gen(n))
    return factors[n]
