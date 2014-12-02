#!/usr/bin/env python
"""
A set of functions for building necklaces of various partitions.
"""

from fractions import gcd, Fraction
from rooted_trees import prod
from primes import divisors, totient
from math import factorial

def nCk(n,k): 
    return int( prod(Fraction(n-i, i+1) for i in range(k)) )

def necklace_totient(partition):
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
    
def necklace_beads(partition):
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
        

if __name__ == '__main__':
    print necklace_totient([4,4,4,3,3,2,1,1])
    print type(necklace_totient([4,4,4,3,3,2,1,1]))
    print nCk(6,3)
    print necklace_beads([4,4,4,3,3,2,1,1])
    print necklace_beads([4,4,4,4,4,6,6,6])
    print necklace_totient([4,4,4,4,4,6,6,6])
    print necklace_beads([24,36])
        
        
