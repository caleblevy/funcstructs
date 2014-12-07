#!/usr/bin/env python
"""
A set of functions for building necklaces of various partitions.
"""

from fractions import gcd, Fraction
from rooted_trees import prod, split_set, forests
from primes import divisors, totient
from math import factorial
from collections import deque

def nCk(n,k): 
    return int( prod(Fraction(n-i, i+1) for i in range(k)) )

def necklace_totient_count(partition):
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
    
def necklace_prime_count(partition):
    k = len(partition)
    N = sum(partition)
    w = reduce(gcd, partition)
    p0 = N/w
    
    factors = divisors(w)
    beads = [0]*factors[-1]
    
    for factor in factors:
        n = period = factor*p0
        beads[factor-1] = 1
        
        for I in range(k):
            beads[factor-1] *= nCk(n, partition[I]*factor/w)
            n -= partition[I]*factor/w
            
        subdivisors = divisors(factor)
        if subdivisors[-1] != 1:
            for subfactor in subdivisors[:-1]:
                beads[factor-1] -= subfactor*p0*beads[subfactor-1]
                
        beads[factor-1] /= period
    return beads
    
necklace_count = necklace_prime_count

def necklace_simple_enumerate(partition, equality=False):
    partition = list(partition)
    a = [0]*sum(partition)
    partition[0] -= 1
    k = len(partition)
    return _necklace_simple_enumerate(a, partition, 2, 1, k, equality=equality)

def _necklace_simple_enumerate(a, partition, t, p, k, equality=False):
    n = len(a)
    if t > n:
        if equality:
            if n == p:
                yield a
        else:
            if n % p == 0:
                yield a
    else:
        r = range(a[t-p-1],k)
        for j in r:
            if partition[j] > 0:
                a[t-1] = j
                partition[j] -= 1
                if j == a[t-p-1]:
                    for z in _necklace_simple_enumerate(a[:],partition,t+1,p,k,equality=equality):
                        yield z
                else:
                    for z in _necklace_simple_enumerate(a[:],partition,t+1,t,k,equality=equality):
                        yield z
                partition[j] += 1

def necklaces(items):
    items = sorted(items)
    y, d = split_set(items)
    for necklace in necklace_simple_enumerate(d):
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
        # cycle.rotate(-1*period)

def cycle_degeneracy(cycle):
    return len(cycle)/periodicity(cycle)

if __name__ == '__main__':
    # print necklace_totient([4,4,4,3,3,2,1,1])
    # print type(necklace_totient([4,4,4,3,3,2,1,1]))
    # print nCk(6,3)
    # print necklace_beads([4,4,4,3,3,2,1,1])
    # print necklace_beads([4,4,4,4,4,6,6,6])
    # print necklace_totient([4,4,4,4,4,6,6,6])
    # print necklace_beads([24,36])
    for I in necklace_simple_enumerate([3,3,2]):
        print I
    print list(necklace_simple_enumerate([3,3]))
    for forest in forests(10):
        if len(list(necklaces(forest))) > 1:
            print '-'*80
            for necklace in necklaces(forest):
                print necklace
    print periodicity([1,1,1,2,3,1,1,1,2,3])
    
        
