#!/usr/bin/env python
# Copyright (C) 2014-2015 Caleb Levy - All Rights Reserved.
# 
# The terms of use, license and copyright information for the code and ideas 
# contained herein are described in the LICENSE file included with this 
# project. For more information please contact me at caleb.levy@berkeley.edu.

"""
Two common kinds of problem in combinatorics are enumeration and counting. In
theory we may view counting as a strict subproblem of enumeration, since
enumerating all elements in a set necessarily allows us to count them.

In practice, there are many tricks one may use to count the number of objects
in a set while performing far less work than listing the elements directly.
This module collects efficient ways of counting endofunction-related objects
without direct enumeration.
"""

from setops import split_set, prod
from iteration import tuple_partitions
from fractions import Fraction
from primes import divisors
from integerroots import isqrt
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
    for b in tuple_partitions(n):
        tot += burnside_partition_degeneracy(b)
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

    def testPartitionNumbers(self):
        counts = [1, 1, 2, 3, 5, 7, 11, 15, 22, 30, 42, 56, 77, 101, 135]
        for n in range(len(counts)):
            self.assertEqual(counts[n], partition_number(n))
            
    def testTreeCounts(self):
        A000081 = [0, 1, 1, 2, 4, 9, 20, 48, 115, 286, 719, 1842, 4766, 12486]
        self.assertEqual(A000081, rooted_treecount_upto(len(A000081)-1))
            

if __name__ == '__main__':
    unittest.main()
    