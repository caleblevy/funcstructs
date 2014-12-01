#!/usr/bin/env python
"""
A set of functions for building necklaces of various partitions.
"""

import fractions
from operator import mul
from rooted_trees import split_set
import unittest

prod = lambda iterable: reduce(mul, iterable, 1)

def prime_factorization(n):
    primfac = []
    d = 2
    while d*d <= n:
        while (n % d) == 0:
            primfac.append(d)  # supposing you want multiple factors repeated
            n /= d
        d += 1
    if n > 1:
       primfac.append(n)
    return primfac
    
prime_divisors = lambda n: list(set(prime_factorization(n)))

def factorGenerator(n):
    primes, multiplicities = split_set(prime_factorization(n))
    factors = []
    for p, d in zip(primes, multiplicities):
        factors.append((p,d,))
    return factors

def divisorGen(n):
    factors = factorGenerator(n)
    nfactors = len(factors)
    f = [0] * nfactors
    while True:
        yield reduce(lambda x, y: x*y, [factors[x][0]**f[x] for x in range(nfactors)], 1)
        i = 0
        while True:
            f[i] += 1
            if f[i] <= factors[i][1]:
                break
            f[i] = 0
            i += 1
            if i >= nfactors:
                return

divisors = lambda n: list(divisorGen(n))

def phi_product(n):
    return n*prod((1 - fractions.Fraction(1,p) for p in prime_divisors(n)))
    

def phi_sum(n):
    phi = 0
    for k in range(1, n + 1):
        if fractions.gcd(n, k) == 1:
            phi += 1
    return phi
    
totient = phi_sum
    

    

if __name__ == '__main__':
    print prod(range(1,5))
    print prime_factorization(12)
    print prime_divisors(12)
    print phi_product(12)
    print totient(12)
    print factorGenerator(12)
    print divisors(12)
    print factorGenerator(24)
    print divisors(24)