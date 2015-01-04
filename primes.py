#!/usr/bin/env python
# Copyright (C) 2014 Caleb Levy - All Rights Reserved.
# 
# The terms of use, license and copyright information for the code and ideas 
# contained herein are described in the LICENSE file included with this 
# project. For more information please contact me at caleb.levy@berkeley.edu.

"""
A collection of short functions for enumerating factorizations of integers and
other such things.
"""
from rooted_trees import prod, split_set
from math import ceil
import fractions
import unittest

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

def factorGenerator(n):
    primes, multiplicities = split_set(prime_factorization(n))
    factors = []
    for p, d in zip(primes, multiplicities):
        factors.append((p,d,))
    return factors

def divisorGen(n):
    """
    Find every divisor of an integer n. Code taken directly from
        "What is the best way to get all the divisors of a number" at
        http://stackoverflow.com/a/171784.
    """
    factors = factorGenerator(n)
    nfactors = len(factors)
    f = [0] * nfactors
    while True:
        yield prod([factors[x][0]**f[x] for x in range(nfactors)])
        i = 0
        while True:
            f[i] += 1
            if f[i] <= factors[i][1]:
                break
            f[i] = 0
            i += 1
            if i >= nfactors:
                return

divisor_list = lambda n: list(divisorGen(n)) if n > 1 else [1]

def divisors_memoized(n, factors={}):
    if n not in factors:
        factors[n] = divisor_list(n)
    return factors[n]

divisors = divisors_memoized

def ceildiv(a, b):
    """Does long integer division taking the ceiling instead of the floor"""
    return -(-a // b)

def isdivisor(d, n):
    if ceildiv(n,d) == n//d:
        return True
    return False

def divisor_sum(n, power=1):
    return sum(map(lambda x: pow(x,power), divisors(n)))
    
def phi_product(n):
    """Return the totient using the fancy prime formula."""
    return int(n*prod((1 - fractions.Fraction(1,p) for p in prime_divisors(n))))
    
def phi_sum(n):
    """Return the totient using its definition. Code taken directly from 
        "Computing Eulers Totient Function" at
        http://stackoverflow.com/a/18114286
    """
    phi = 0
    for k in range(1, n + 1):
        if fractions.gcd(n, k) == 1:
            phi += 1
    return int(phi)
    
totient = phi_sum

class PrimeTest(unittest.TestCase):
    def testPrimeDivisorsRepeated(self):
        """OEIS A001222: number of prime divisors with multiplicity."""
        counts = [0, 1, 1, 2, 1, 2, 1, 3, 2, 2, 1, 3, 1, 2, 2, 4, 1, 3, 1, 3, \
                  2, 2, 1, 4, 2, 2, 3, 3, 1, 3]
        for I in range(1,len(counts)+1):
            self.assertEqual(counts[I-1],len(prime_factorization(I)))
            
    def testPrimeDivisorsNonrepeated(self):
        """OEIS A001221: number of prime divisors without multiplicity."""
        counts = [0, 1, 1, 1, 1, 2, 1, 1, 1, 2, 1, 2, 1, 2, 2, 1, 1, 2, 1, 2, \
                  2, 2, 1, 2, 1, 2, 1, 2, 1, 3]
        for I in range(1,len(counts)+1):
            self.assertEqual(counts[I-1],len(prime_divisors(I)))
    
    def testDivisors(self):
        """OEIS A000005: number of divisors."""
        counts = [1, 2, 2, 3, 2, 4, 2, 4, 3, 4, 2, 6, 2, 4, 4, 5, 2, 6, 2, 6, \
                  4, 4, 2, 8, 3, 4, 4, 6, 2, 8]
        for I in range(1,len(counts)+1):
            self.assertEqual(counts[I-1],len(divisors(I)))
            # Check twice, see if its been memoized properly.
            self.assertEqual(counts[I-1],len(divisors(I)))
    
    def testCeildiv(self):
        N = 20
        for I in range(-N,0)+range(1,N+1):
            for J in range(-N,0)+range(1,N+1):
                self.assertEqual(ceildiv(I,J), ceil(1.*I/J))
    
    def testIsDivisor(self):
        N = 20
        for I in range(1,N):
            for J in range(1,N):
                self.assertEqual(J in divisors(I), isdivisor(J,I))
                
    def testDivisorSigma(self):
        """Test sums of powers of divisors. Features:
            -OEIS A000005: divisor_sum(n,0)
            -OEIS A000203: divisor_sum(n,1)
            -OEIS A001157: divisor_sum(n,2)
            -OEIS A001158: divisor_sum(n,3)
        """
        sums = [ [1, 2, 2, 3, 2, 4, 2, 4, 3, 4, 2, 6],
                 [1, 3, 4, 7, 6, 12, 8, 15, 13, 18],
                 [1, 5, 10, 21, 26, 50, 50, 85, 91, 130],
                 [1, 9, 28, 73, 126, 252, 344, 585, 757, 1134] ]
        for power, seq in enumerate(sums):
            for n, tot in enumerate(seq):
                self.assertEqual(tot, divisor_sum(n+1,power))
        
    def testTotients(self):
        """OEIS A000010: number of relatively prime smaller integers."""
        values = [1, 1, 2, 2, 4, 2, 6, 4, 6, 4, 10, 4, 12, 6, 8, 8, 16, 6, 18, \
                  8, 12, 10, 22, 8, 20, 12, 18]
        for I in range(1,len(values)+1):
            self.assertEqual(values[I-1], phi_product(I))
            self.assertEqual(values[I-1], phi_sum(I))
        
if __name__ == '__main__':
    unittest.main()