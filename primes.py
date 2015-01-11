#!/usr/bin/env python
# Copyright (C) 2014-2015 Caleb Levy - All Rights Reserved.
# 
# The terms of use, license and copyright information for the code and ideas 
# contained herein are described in the LICENSE file included with this 
# project. For more information please contact me at caleb.levy@berkeley.edu.

"""
A collection of short functions for enumerating factorizations of integers and
other such things.
"""
from setops import prod, split_set
from iteration import product_range
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

                
def divisorGen(n):
    """
    Find every divisor of an integer n. Code inspired by
        "What is the best way to get all the divisors of a number" at
        http://stackoverflow.com/a/171784.
    """
    factors, powers = split_set(prime_factorization(n))
    # Since the factors are prime, every unique partition of powers represents 
    # a different divisor.
    for power_combo in product_range([m+1 for m in powers]):
        yield prod([factors[I]**p for I, p in enumerate(power_combo)])

divisor_list = lambda n: list(divisorGen(n))

def divisors_memoized(n, factors={}):
    if n not in factors:
        factors[n] = divisor_list(n)
    return factors[n]

divisors = divisors_memoized


def divisor_sum(n, power=1):
    return sum(map(lambda x: pow(x,power), divisors(n)))


def ceildiv(a, b):
    """Does long integer division taking the ceiling instead of the floor"""
    return -(-a // b)

def isdivisor(d, n):
    if ceildiv(n,d) == n//d:
        return True
    return False
    
    
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
            self.assertEqual(counts[I-1], len(prime_factorization(I)))
            
    def testPrimeDivisorsNonrepeated(self):
        """OEIS A001221: number of prime divisors without multiplicity."""
        counts = [0, 1, 1, 1, 1, 2, 1, 1, 1, 2, 1, 2, 1, 2, 2, 1, 1, 2, 1, 2, \
                  2, 2, 1, 2, 1, 2, 1, 2, 1, 3]
        for I in range(1,len(counts)+1):
            self.assertEqual(counts[I-1], len(prime_divisors(I)))
    
    def testDivisorCount(self):
        """OEIS A000005: number of divisors."""
        A000005 = [1, 2, 2, 3, 2, 4, 2, 4, 3, 4, 2, 6, 2, 4, 4, 5, 2, 6, 2, 6, \
                  4, 4, 2, 8, 3, 4, 4, 6, 2, 8]
        for I, divcount in enumerate(A000005):
            self.assertEqual(divcount, len(divisors(I+1)))
            self.assertEqual(divcount, len(divisors(I+1)))
    
    def testCeildiv(self):
        N = 20
        divrange = list(range(-N,0))+list(range(1,N+1))
        for I in divrange:
            for J in divrange:
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