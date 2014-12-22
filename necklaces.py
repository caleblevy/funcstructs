#!/usr/bin/env python
"""
A set of functions for building necklaces of various partitions.
"""

from fractions import gcd, Fraction
from rooted_trees import prod, split_set
from primes import divisors, totient
from math import factorial
from collections import deque
import unittest

def nCk(n,k): 
    """Binomial coefficient (n k) = n choose k."""
    return factorial(n)/factorial(k)/factorial(n-k)

def necklace_count_totient(partition):
    k = len(partition)
    n = sum(partition)
    w = reduce(gcd, partition)
    
    factors = divisors(w)
    m = len(factors)
    beads = [0]*m
    
    for I in range(m):
        beads[I] = Fraction(totient(factors[I])*factorial(n/factors[I]),n)
        for J in range(k):
            beads[I] /= factorial(partition[J]/factors[I])

    return int(sum(beads))
    
def partition_necklace_count_by_periodicity(partition):
    k = len(partition)
    N = sum(partition)
    w = reduce(gcd, partition)
    p0 = N/w
    
    factors = divisors(w)
    beads = [0]*factors[-1]
    
    for factor in factors:
        n = period = factor*p0
        beads[factor-1] = 1
        
        for I in xrange(k):
            beads[factor-1] *= nCk(n, partition[I]*factor/w)
            n -= partition[I]*factor/w
            
        subdivisors = divisors(factor)
        if subdivisors[-1] != 1:
            for subfactor in subdivisors[:-1]:
                beads[factor-1] -= subfactor*p0*beads[subfactor-1]
                
        beads[factor-1] /= period
    return beads
    
def necklace_count_by_periodicity(items):
    _, partition = split_set(items)
    return partition_necklace_count_by_periodicity(partition)

necklace_count = lambda items: sum(necklace_count_by_periodicity(items))

def partition_necklaces(partition):
    partition = list(partition)
    a = [0]*sum(partition)
    partition[0] -= 1
    k = len(partition)
    return _partition_necklaces(a, partition, 2, 1, k)

def _partition_necklaces(a, partition, t, p, k):
    n = len(a)
    if t > n and not(n % p):
        yield a
    else:
        for j in xrange(a[t-p-1],k):
            if partition[j] > 0:
                a[t-1] = j
                partition[j] -= 1
                tp = p if(j == a[t-p-1]) else t
                for z in _partition_necklaces(a,partition,t+1,tp,k):
                    yield z
                partition[j] += 1

def necklaces(items):
    """
    Given a set of items (called beads) returns all necklaces which can be made
    with those beads.
    """
    if not items:
        return
    items = sorted(items)
    y, d = split_set(items)
    for necklace in partition_necklaces(d):
        # Explicitly make a tuple, since we must form the list of all necklaces in memory when constructing endofunction structures.
        yield tuple([y[I] for I in necklace])
    
def periodicity(cycle):
    orig = deque(cycle)
    cycle = deque(cycle)
    period_prev = 0
    for period in divisors(len(cycle)):
        cycle.rotate(period - period_prev)
        period_prev = period
        if orig == cycle:
            return period
        
def cycle_degeneracy(cycle):
    return len(cycle)/periodicity(cycle)

class NecklaceTests(unittest.TestCase):    
    def testPeriodicities(self):
        N = 20
        for n in range(1,N+1):
            for d in divisors(n):
                # Creates lists of each periodicity
                period_dn = ([0]+[1]*(d-1))*(n/d)
                self.assertEqual(d, periodicity(period_dn))
                
    def testNecklaces(self):
        beadsets = [[4,4,5,5,2,2,2,2,2,2,6,6], [4,4,5,5,2,2,2,2,2,2,6,6,6], [0]]
        for beadset in beadsets:
            count = 0
            for necklace in necklaces(beadset):
                count += 1
            self.assertEqual(necklace_count(beadset), count)
        
if __name__ == '__main__':
    # print necklace_totient([4,4,4,3,3,2,1,1])
    # print necklace_beads([4,4,4,4,4,6,6,6])
    # print necklace_totient([4,4,4,4,4,6,6,6])
    # print necklace_beads([24,36])
    # for I in necklace_simple_enumerate([3,3,2]):
    unittest.main()
        
