from itertools import product
from collections import Iterable
from time import time
import unittest

def product_range(start, stop=None, step=None):
    """
    Nice wrapper for itertools.product. Give it a tuple of dimension lengths and it will return 
    """
    if stop is None:
        start, stop = stop, start
    # If start is not iterable, it is either an int or none.
    if not isinstance(start, Iterable):
        start = 0 if not start else start
        start = [start]*len(stop)        
    if not isinstance(step, Iterable):
        step = 1 if not step else step
        step = [step]*len(stop)
    if not len(start) == len(step) == len(stop):
        raise ValueError("Start, stop and step tuples must all be the same length.")
    return product(*[range(I,J,K) for I,J,K in zip(start,stop,step)])

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
        
def _minimal_partition(n,L): 
    h = n/L
    err = n - L*h
    bas = L - err
    j = bas + 1
    if h <> 1:
        j = 1
    return [h+1]*err + [h]*bas, j

def minimal_partition(n,L):
    min_part, _ = _minimal_partition(n,L)
    return min_part     

def fixed_lex_partitions(n,L):
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
        
    partition, j = _minimal_partition(n,L)
    while True:
        yield partition                   
        k = 2
        s = (j-1) + partition[L-j] - 1
        while partition[L-j-k] == partition[L-j-1] and j+k-1<L:
            s += partition[L-j-1]
            k += 1            
        if j+k-1 > L:
            return                        
        k -= 1
        partition[L-j-k] += 1
        partition[L-j-k+1:L], j = _minimal_partition(s,j+k-1)     

def compositions_simple(n):
    comp = [n]
    while True:
        yield comp
        J = len(comp)
        if J == n:
            return
        for K in range(J,0,-1):
            # Keep descending (backwards) until hitting a "step" you can subtract from
            if comp[K-1]-1 != 0:
                comp[K-1] -= 1
                comp.append(J-K+1)
                break
            # Haven't hit the target, pop the last element, and step back
            comp.pop()

compositions = compositions_simple # best by test.

class IterationTest(unittest.TestCase):
    
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
                
if __name__ == '__main__':
    unittest.main()
