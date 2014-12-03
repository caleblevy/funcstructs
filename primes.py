#!/usr/bin/env python
"""
A set of functions for building necklaces of various partitions.
"""

import fractions
from rooted_trees import prod, split_set
import unittest

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

divisors = lambda n: list(divisorGen(n)) if n > 1 else [1]

def phi_product(n):
    return int(n*prod((1 - fractions.Fraction(1,p) for p in prime_divisors(n))))
    
def phi_sum(n):
    phi = 0
    for k in range(1, n + 1):
        if fractions.gcd(n, k) == 1:
            phi += 1
    return int(phi)
    
totient = phi_sum

# If run standalone, perform unit tests
class PrimeTest(unittest.TestCase):
    def testPrimeDivisorsRepeated(self):
        """Test number of prime divisors with multiplicity. See OEIS A001222."""
        counts = [0, 1, 1, 2, 1, 2, 1, 3, 2, 2, 1, 3, 1, 2, 2, 4, 1, 3, 1, 3, 2, 2, 1, 4, 2, 2, 3, 3, 1, 3]
        for I in range(1,len(counts)+1):
            self.assertEqual(counts[I-1],len(prime_factorization(I)))
            
    def testPrimeDivisorsNonrepeated(self):
        """Test number of prime divisors without multiplicity. See OEIS A001221."""
        counts = [0, 1, 1, 1, 1, 2, 1, 1, 1, 2, 1, 2, 1, 2, 2, 1, 1, 2, 1, 2, 2, 2, 1, 2, 1, 2, 1, 2, 1, 3]
        for I in range(1,len(counts)+1):
            self.assertEqual(counts[I-1],len(prime_divisors(I)))
    
    def testDivisors(self):
        """Test number of divisors. See OEIS A000005."""
        counts = [1, 2, 2, 3, 2, 4, 2, 4, 3, 4, 2, 6, 2, 4, 4, 5, 2, 6, 2, 6, 4, 4, 2, 8, 3, 4, 4, 6, 2, 8]
        for I in range(1,len(counts)+1):
            self.assertEqual(counts[I-1],len(divisors(I)))
        
    def testTotients(self):
        '''Test values of the totient function. See OEIS A000010.'''
        values = [1, 1, 2, 2, 4, 2, 6, 4, 6, 4, 10, 4, 12, 6, 8, 8, 16, 6, 18, 8, 12, 10, 22, 8, 20, 12, 18]
        for I in range(1,len(values)+1):
            self.assertEqual(values[I-1], phi_product(I))
            self.assertEqual(values[I-1], phi_sum(I))
        
        
        
    
if __name__ == '__main__':
    unittest.main()