from itertools import product
from collections import Iterable
import unittest

def product_range(start, stop=None, step=None, iteration_order=None):
    """
    Nice wrapper for itertools.product. Give it a tuple of dimension lengths and it will return 
    """
    if stop is None:
        start, stop = stop, start
    # If start is not iterable, it is either an int or none. Don't be a dick.
    if not isinstance(start, Iterable):
        start = 0 if not start else start
        start = [start]*len(stop)        
    if not isinstance(step, Iterable):
        step = 1 if not step else step
        step = [step]*len(stop)
    if not len(start) == len(step) == len(stop):
        raise ValueError("Start, stop and step tuples must all be the same length.")
    return product(*[range(I,J,K) for I,J,K in zip(start,stop,step)])

def compositions(n):
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

print minimal_partition(10,10)
for I in fixed_lex_partitions(40,7):
    print I


        
