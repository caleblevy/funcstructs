from itertools import product
from collections import Iterable
from time import time
import unittest

def product_range(start, stop=None, step=None):
    """
    Nice wrapper for itertools.product. Give it a tuple of starts, stops and increments and it will return the nested
    for loop coresponding to them. I.E. if start = (r1,r2,...,rn), stop = (s1,s2,...,sn) and step = (t1,t2,...,tn) then
    
        for tup in product_range(start,stop,step):
            yield tup
        
    is equivalent to:
    
        for I1 in range(r1,s1,t1):
          for I2 in range(r2,s2,t2):
            ...
              for In in range(rn,sn,tn):
                yield tuple(I1,I2,...,In)
    
    If stop==step==None then start is treated as stop and step is set by default to 1 and start to 0. If start and step
    are integers they are transformed into start = [start]*len(stop) and step = [step]*len(step).
    """
    if stop is None:
        start, stop = stop, start
    # If start is not iterable, it is either an int or none.
    if not isinstance(start, Iterable):
        start = 0 if(start is None) else start
        start = [start]*len(stop)        
    if not isinstance(step, Iterable):
        step = 1 if(step is None) else step
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

def compositions_simple(n):
    comp = [n]
    while True:
        yield comp
        J = len(comp)
        if J == n:
            return
        for K in xrange(J-1,-1,-1):
            # Keep descending (backwards) until hitting a "step" you can subtract from
            if comp[K] is not 1:
                comp[K] -= 1
                comp.append(J-K)
                break
            # Haven't hit the target, pop the last element, and step back
            comp.pop()

compositions = compositions_simple # best by test.

def _min_part(n,L): 
    h = n/L
    err = n - L*h
    bas = L - err
    j = bas + 1
    if h <> 1:
        j = 1
    return [h+1]*err + [h]*bas, j

def minimal_partition(n,L):
    min_part, _ = _min_part(n,L)
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
        
    partition, j = _min_part(n,L)
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
        partition[L-j-k+1:L], j = _min_part(s,j+k-1)     

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
