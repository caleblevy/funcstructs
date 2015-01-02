#!/usr/bin/env python
# Copyright (C) 2014 Caleb Levy - All Rights Reserved.
# 
# The terms of use, license and copyright information for the code and ideas 
# contained herein are described in the LICENSE file included with this 
# project. For more information please contact me at caleb.levy@berkeley.edu.

"""
A collection of miscellaneous generator functions that do not fit elsewhere.
"""

from PADS.IntegerPartitions import partitions, lex_partitions
from collections import Iterable
from rooted_trees import prod
from itertools import product
import unittest

def parse_ranges(start, stop, step):
    """
    If stop==step==None then start is treated as stop and step is set by
    default to 1 and start to 0. If start and step are integers they are
    transformed into start = [start]*len(stop) and step = [step]*len(step).
    """
    if stop is None:
        start, stop = stop, start
    # If start is not iterable, it is either an int or none.
    if not isinstance(start, Iterable):
        start = [0 if(start is None) else start]*len(stop)
    if not isinstance(step, Iterable):
        step = [1 if(step is None) else step]*len(stop)
    if not len(start) == len(step) == len(stop):
        raise ValueError("start, stop and step must all be same length.")
    return start, stop, step

def product_range(start, stop=None, step=None):
    """
    Nice wrapper for itertools.product. Give it a tuple of starts, stops and
    increments and it will return the nested for loop coresponding to them.
    I.E. if start = (r1,r2,...,rn), stop = (s1,s2,...,sn) and step =
    (t1,t2,...,tn) then
    
        for tup in product_range(start,stop,step):
            yield tup
        
    is equivalent to:
    
        for I1 in range(r1,s1,t1):
          for I2 in range(r2,s2,t2):
            ...
              for In in range(rn,sn,tn):
                yield tuple(I1,I2,...,In)
    """
    start, stop, step = parse_ranges(start, stop, step)
    return product(*[range(I,J,K) for I,J,K in zip(start,stop,step)])


def tuple_partitions(n):
    """
    Every partition on N may be represented in the form as a tuple of numbers
    (n1,n2,...,nk) with 1<=i<=k such that 1*n1+2*n2+...+k*nk=N.
    
    This program outputs every partition of n in a tuple format.
    """
    for part in partitions(n):
        b = [0]*n
        for p in part:
            b[p-1] += 1
        yield b


def compositions_binary(n):
    """Additive compositions of a number; i.e. partitions with ordering."""
    for binary_composition in product_range([2]*(n-1)):
        tot = 1
        composition = []
        for I in binary_composition:
            if I:
                composition.append(tot)
                tot = 1
                continue
            tot += 1
        composition.append(tot)
        yield composition
    
    
def compositions_simple(n):
    """A more direct way of enumerating compositions."""
    comp = [n]
    while True:
        yield comp
        J = len(comp)
        if J == n:
            return
        for K in range(J-1,-1,-1):
            # Keep descending (backwards) until hitting a "step" you can 
            # subtract from
            if comp[K] is not 1:
                comp[K] -= 1
                comp.append(J-K)
                break
            # Haven't hit the target, pop the last element, and step back
            comp.pop()
    
compositions = compositions_simple # best by test.


def _min_part(n,L):
    """
    Helper function for fixed_lex_partitions. Returns a tuple containing:
        1) The output of minimal_partition(n,L)
        2) #(Occurances of 1 in this partition)+1.

    The second output is returned so as to avoid calling the count() method of
    the list corresponding to the partition, since this information is
    necessarily contained in the process of its creation. It is needed by
    fixed_lexed_partitions for the index on which to decrement.
    """
    
    binsize = n//L 
    overstuffed = n - L*binsize 
    regular = L - overstuffed
    ones_count = 1 if binsize != 1 else regular + 1
    return [binsize+1]*overstuffed + [binsize]*regular, ones_count


def minimal_partition(n,L):
    """
    A wrapper for _min_partition. Given integers n > 0 and L <= n, returns the
    lexicographically smallest unordered integer partition of n into L nonzero
    parts.
    """
    min_part, _ = _min_part(n,L)
    return min_part     


def fixed_lex_partitions(n,L):
    """
    Integer partitions of n into L parts, in lexicographic order. This
    algorithm was derived and implemented by Caleb C. Levy in 2014. Its form
    was taken from David Eppstein's equivalent generator for fixed length
    partitions in colex order.
    """
    
    if L == 0:
        if n == 0:
            yield []
        return
    if L == 1:
        if n > 0:
            yield [n]
        return
    if n < L:
        return
        
    partition, j = _min_part(n,L)
    while True:
        # Algorithm starts with minimal partition, and index of the last 1 
        # counting backwards. We then decrement the rightmost components and 
        # increment those to their immediate left, up to the point where the 
        # partition would beak ordering.
        #
        # Once we have decremented as far as possible, we append the new 
        # minimum partition, and repeat.
        yield partition                   
        k = 2
        s = (j-1) + partition[L-j] - 1
        while j+k-1 < L and partition[L-j-k] == partition[L-j-1]:
            s += partition[L-j-1]
            k += 1            
        if j+k-1 > L:
            return                        
        k -= 1
        partition[L-j-k] += 1
        partition[L-j-k+1:L], j = _min_part(s,j+k-1)   


def inv(perm):
    """Invert a permutation of integers I=1...n. """
    inverse = [0] * len(perm)
    for i, p in enumerate(perm):
        inverse[p] = i
    return inverse 


class IterationTest(unittest.TestCase):
    
    def testProductRange(self):
        starts = [None,   0,      1,      (1,)*4,  (3,)*4, (1,2,3,3)]
        stops =  [(4,)*4, (4,)*4, (7,)*3, (10,)*4, (6,)*4, (2,4,8,10)]
        steps =  [1,      None,   2,      3,       None,   (1,1,2,2)]
        
        counts = [4**4,   4**4,   3**3,   3**4,    3**4,   1*2*3*4]
        for count, start, stop, step in zip(counts, starts, stops, steps):
            self.assertEqual(count, len(list(product_range(start, stop, step))))
            self.assertEqual(prod(stop), len(list(product_range(stop)))) 
            
            
    def testCompositionCounts(self):
        for n in range(1,10):
            self.assertEqual(2**(n-1), len(list(compositions_simple(n))))
            self.assertEqual(2**(n-1), len(list(compositions_binary(n))))
            
            
    def testCompositionSums(self):
        for n in range(1,10):
            for comp in compositions_simple(n):
                self.assertEqual(n, sum(comp))
            for comp in compositions_binary(n):
                self.assertEqual(n, sum(comp))
    
    
    def testSmallestPartition(self):
        N = 20
        for n in range(1,N):
            for L in range(1,n+1):
                mp = minimal_partition(n,L)
                self.assertTrue(max(mp) - min(mp) in [0,1])
                self.assertTrue(len(mp) == L)
                self.assertTrue(sum(mp) == n)


    def testFixedLexPartitions(self):
        """Check that the fixed length lex partition outputs are correct."""
        N = 15
        for n in range(N):
            pn = [list(p) for p in lex_partitions(n)]
            np = 0
            for L in range(n+1):
                pnL = [list(p) for p in fixed_lex_partitions(n,L)]
                np += len(pnL)
                # Check for the right order
                self.assertEqual(pnL,[p for p in pn if len(p) == L])
            # Check for the right number
            self.assertEqual(np,len(pn))
                
                
if __name__ == '__main__':
    unittest.main()
