#!/usr/bin/env python
"""
When you were in first grade you may have gotten to play with strings and a bucket of beads of different shapes and colors. By stringing together different colored beads and tying the ends of the rope together you could make different necklaces. You can wear necklaces in different ways by rotating them.

Mathematically, a necklace is a class of n-character strings equivalent under
rotation (orbits of the set of n-character strings under the action of cyclic
permutation by the cyclic group). For example, the following are examples of a
necklace using [a,b,c,d], [a,b,b] and [c,d]:

    [a,b,c,d] ~ [b,c,d,a] ~ [c,d,a,b] ~ [d,a,b,c]
    [a,b,b] ~ [b,a,b] ~ [b,b,a]
    [c,d,c,d] ~ [d,c,d,c]

Different necklaces may have different periodicity, as seen above. This module
contains a collection of functions for counting and enumerating necklaces of a
given multiset.

Their relavence to enumerating endofunction structures is as follows: given a
collection of N forests, the necklaces whose beads are the forest's trees are
precisely the distinct ways of connecting the trees to form a cycle of length
n. Thus the ways of connecting a collection of rooted trees together in a cycle
are precisely the necklaces whose beads are the rooted trees.
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

# We may canonically represent a multiset with an unordered partition corresponding to the multiplicities of the elements. It is simpler to enumerate necklaces on a canonical partition and then match those to necklaces formed from the beads.

def necklace_count_totient(partition):
    """
    A common formula, found on Wikipedia, giving the number of necklaces
    corresponding to a given partition of multiplicities.
    """
    k = len(partition)
    n = sum(partition)
    w = reduce(gcd, partition)
    
    factors = divisors(w)
    m = len(factors)
    beads = [0]*m
    
    for I in xrange(m):
        beads[I] = Fraction(totient(factors[I])*factorial(n/factors[I]),n)
        for J in xrange(k):
            beads[I] /= factorial(partition[J]/factors[I])

    return int(sum(beads))
    
    
def partition_necklace_count_by_periodicity(partition):
    """
    Given a partition of multiplicities, returns the number of necklaces on
    this partition of beads of each possible period of the necklace. To this,
    we start with the smallest divisor of the gcd of all the multiplicities,
    and find all necklaces with period less than or equal to this divisor.
    
    Before normalizing by the period of the necklace (to account for its
    distinct rotations) we subtract the number of necklaces with each period
    which is a subdivisor of our given period, to ensure we give the number of
    necklaces with exactly period k.
    """
    k = len(partition)
    N = sum(partition)
    w = reduce(gcd, partition)
    p0 = N/w
    
    factors = divisors(w)
    beads = [0]*factors[-1]
    
    # Find the multiplicity of each period
    for factor in factors:
        n = period = factor*p0
        beads[factor-1] = 1
        # The number of character permutations is simply the multinomial coefficient corresponding to that subset of the multiplicity partition.
        for I in xrange(k):
            beads[factor-1] *= nCk(n, partition[I]*factor/w)
            n -= partition[I]*factor/w
            
        # Subtact off the number of necklaces whose period subdivides our divisor of w, to make sure beads[factor-1] give the EXACTLY the number of necklaces with period k.
        subdivisors = divisors(factor)
        if subdivisors[-1] != 1:
            for subfactor in subdivisors[:-1]:
                beads[factor-1] -= subfactor*p0*beads[subfactor-1]
        # Finally, normalize by the period, the number of distinct rotations of any member of beads[k].
        beads[factor-1] /= period
    return beads
    
    
def necklace_count_by_periodicity(beads):
    """
    Returns a list whose kth element is the number of necklaces corresponding
    to the input set of beads with k+1 distinct rotations.
    """
    _, partition = split_set(beads)
    return partition_necklace_count_by_periodicity(partition)


necklace_count = lambda items: sum(necklace_count_by_periodicity(items))


def partition_necklaces(partition):
    """ 
    Wrapper for partition necklaces, which takes a partition of multiplicities
    and enumerates canonical necklaces on that partition.
    """
    partition = list(partition)
    a = [0]*sum(partition)
    partition[0] -= 1
    k = len(partition)
    return _partition_necklaces(a, partition, 2, 1, k)

def _partition_necklaces(a, partition, t, p, k):
    """
    This function is a result of refactoring of Sage's _simple_fixed_content
    algorithm, featured in Sage at https://github.com/sagemath/sage.git,
    located in src/sage/combinat/neckalce.py as of December 23, 2014.
    
    The original code was written by Mike Hansen <mhansen@gmail.com> in 2007,
    who based his algorithm on
    
        Sawada, Joe. "A fast algorithm to generate necklaces with fixed
        content", Theoretical Computer Science archive Volume 301 , Issue 1-3,
        May 2003.
    """
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
    """
    Find the "periodicity" of a list; i.e. the number of its distinct cyclic
    rotations. To do this, represent the cycle as a queue, and rotate the queue
    by the divisors of its length until they are equal. The first occurance of
    this is the period.
    """
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
                
    def testNecklaceCounts(self):
        color_partitions = [[24,36], [3,3,2], [4,4,4,3,3,2,1,1]]
        color_cardinalities = [600873126148801, 70, 51330759480000]
        for cp, cc in zip(color_partitions, color_cardinalities):
            self.assertEqual(cc, necklace_count_totient(cp))
            self.assertEqual(cc,
                             sum(partition_necklace_count_by_periodicity(cp)))
        
    def testNecklaces(self):
        beadsets = [[4,4,5,5,2,2,2,2,2,2,6,6], [4,4,5,5,2,2,2,2,2,2,6,6,6], [0]]
        for beadset in beadsets:
            count = 0
            for necklace in necklaces(beadset):
                count += 1
            self.assertEqual(necklace_count(beadset), count)
        
if __name__ == '__main__':
    unittest.main()
        
