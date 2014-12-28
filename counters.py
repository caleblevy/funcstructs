#!/usr/bin/env python
# Copyright (C) 2014 Caleb Levy - All Rights Reserved.
# 
# The terms of use, license and copyright information for the code and ideas 
# contained herein are described in the LICENSE file included with this 
# project. For more information please contact me at caleb.levy@berkeley.edu.

from primes import divisors
from rooted_trees import split_set, prod
from PADS.IntegerPartitions import partitions
from itertools import chain
from math import factorial
from fractions import Fraction
import unittest

def binary_partitions(n):
    for part in partitions(n):
        b = [0]*n
        for p in part:
            b[p-1] += 1
        yield b

def burnside_partition_degeneracy(b):
    product_terms = []
    for i in range(1,len(b)+1):
        s = 0
        for j in divisors(i):
            s += j*b[j-1]
        s **= b[i-1]
        t = Fraction(i,1)
        t **= (-1*b[i-1])
        s *= t
        s /= factorial(b[i-1])
        product_terms.append(s)
    return prod(product_terms)
        
def funcstruct_count(n):
    tot = 0
    for bp in binary_partitions(n):
        tot += burnside_partition_degeneracy(bp)
    return int(tot)

def ceildiv(a, b):
    """Does long integer division taking the ceiling instead of the floor"""
    return -(-a // b)

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
    # Iterate over the pentagonal numbers. Formula from http://mathworld.wolfram.com/PartitionFunctionP.html
    if N == 0:
        return [1]
    P = [1]+[0]*N
    for n in range(1,N+1):
        k_max = (isqrt(24*n+1)-1)//6
        k_min = -1*((isqrt(24*n+1)+1)//6)
        for k in chain(range(k_min,0),range(1,k_max+1)):
            pk = k*(3*k+1)
            P[n] += (-1)**abs((k-1)) * P[n-pk//2]
    return P

partition_number = lambda n: partition_numbers_upto(n)[-1]

class CounterTest(unittest.TestCase):
    def testEndofunctionStructureCount(self):
        counts = [1, 1, 3, 7, 19, 47, 130, 343, 951, 2615, 7318, 20491, 57903]
        for n in range(len(counts)):
            self.assertEqual(counts[n], funcstruct_count(n))
            
    def testIntegerRoots(self):
        for val in chain(range(1000),range(2**96,2**96+100)):
            for power in range(1,5):
                self.assertTrue(iroot(val,power)**power <= val)
                self.assertTrue(val < (iroot(val,power)+1)**power)
                
                self.assertTrue(iroot_newton(val,power)**power <= val)
                self.assertTrue(val < (iroot_newton(val,power)+1)**power)
    
    def testPartitionNumbers(self):
        counts = [1, 1, 2, 3, 5, 7, 11, 15, 22, 30, 42, 56, 77, 101, 135]
        for n in range(len(counts)):
            self.assertEqual(counts[n], partition_number(n))
            

if __name__ == '__main__':
    unittest.main()
    