#!/usr/bin/env python
# Copyright (C) 2014 Caleb Levy - All Rights Reserved.
# 
# The terms of use, license and copyright information for the code and ideas 
# contained herein are described in the LICENSE file included with this 
# project. For more information please contact me at caleb.levy@berkeley.edu.

from setops import split_set, prod
from iteration import tuple_partitions
from fractions import Fraction
from primes import divisors
from itertools import chain
from math import factorial
import unittest

def burnside_partition_degeneracy(b):
    product_terms = []
    for I in range(1,len(b)+1):
        s = 0
        for J in divisors(I):
            s += J*b[J-1]
        s **= b[I-1]
        s *= Fraction(I,1)**(-b[I-1])/factorial(b[I-1])
        product_terms.append(s)
    return prod(product_terms)
        
def funcstruct_count(n):
    tot = 0
    for bp in tuple_partitions(n):
        tot += burnside_partition_degeneracy(bp)
    return int(tot)


def rooted_treecount_upto(N):
    if N == 0:
        return [0]
    if N == 1:
        return [0,1]
    T = [0,1]+[0]*(N-1)
    for n in range(2,N+1):
        for I in range(1,n):
            s = 0
            for d in divisors(I):
                s += T[d]*d
            s *= T[n-I]
            T[n] += s
        T[n] //= (n-1)
    return T

rooted_treecount = lambda n: rooted_treecount_upto(n)[-1]
    
                
def iroot_newton(n, k=2):
    """
    Given input integer n, return the greatest integer whose kth power is less
    than or equal to n. This algorithm works by Newton's method.
    
    Code taken directly from 
        "How to find integer nth roots?" at http://stackoverflow.com/a/15979957.
    """
    if not n:
        return 0
    u, s = n, n+1
    while u < s:
        s = u
        t = (k-1) * s + n // pow(s, k-1)
        u = t // k
    return s
    
def iroot(n, k=2):
    """
    Given input integer n, return the greatest integer whose kth power is less
    than or equal to n. This algorithm works by binary search.
    
    Code taken directly from 
        "How to find integer nth roots?" at http://stackoverflow.com/a/15979957.
    """
    hi = 1
    while pow(hi, k) < n:
        hi *= 2
    lo = hi // 2
    while hi - lo > 1:
        mid = (lo + hi) // 2
        midToK = pow(mid, k)
        if midToK < n:
            lo = mid
        elif n < midToK:
            hi = mid
        else:
            return mid
            
    if pow(hi, k) == n:
        return hi
    else:
        return lo

def isqrt(n):
    """
    Faster method of iroot for the particular case of the integer square root.
    
    Code taken directly from 
        "Integer square root in python" at http://stackoverflow.com/a/15391420.
    """
    x = n
    y = (x + 1) // 2
    while y < x:
        x = y
        y = (x + n // x) // 2
    return x
        
def partition_numbers_upto(N):
    # Iterate over the pentagonal numbers. Formula from 
    # http://mathworld.wolfram.com/PartitionFunctionP.html
    if N == 0:
        return [1]
    P = [1]+[0]*N
    for n in range(1,N+1):
        k_max = (isqrt(24*n+1)-1)//6
        k_min = -((isqrt(24*n+1)+1)//6)
        for k in chain(range(k_min,0),range(1,k_max+1)):
            P[n] += (-1)**abs((k-1)) * P[n-k*(3*k+1)//2]
    return P

partition_number = lambda n: partition_numbers_upto(n)[-1]

class CounterTest(unittest.TestCase):
    def testEndofunctionStructureCount(self):
        counts = [1, 1, 3, 7, 19, 47, 130, 343, 951, 2615, 7318, 20491, 57903]
        for n in range(len(counts)):
            self.assertEqual(counts[n], funcstruct_count(n))
            
    def testIntegerRoots(self):
        for val in chain(range(1000),[2**96]):
            for power in range(1,5):
                self.assertTrue(iroot(val,power)**power <= val)
                self.assertTrue(val < (iroot(val,power)+1)**power)
                
                self.assertTrue(iroot_newton(val,power)**power <= val)
                self.assertTrue(val < (iroot_newton(val,power)+1)**power)

    def testPartitionNumbers(self):
        counts = [1, 1, 2, 3, 5, 7, 11, 15, 22, 30, 42, 56, 77, 101, 135]
        for n in range(len(counts)):
            self.assertEqual(counts[n], partition_number(n))
            
    def testTreeCounts(self):
        A000081 = [0, 1, 1, 2, 4, 9, 20, 48, 115, 286, 719, 1842, 4766, 12486]
        self.assertEqual(A000081, rooted_treecount_upto(len(A000081)-1))
            

if __name__ == '__main__':
    unittest.main()
    