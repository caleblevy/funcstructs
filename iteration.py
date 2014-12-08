from itertools import product, combinations, chain
from collections import Iterable
from eppstein.IntegerPartitions import fixed_length_partitions, conjugate
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
    if not len(start) == len(setp) == len(stop):
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

endofunctions = lambda n: product_range([n]*n) 

def partition1(iterable, chain=chain, map=map):
    s = iterable if hasattr(iterable, '__getslice__') else tuple(iterable)
    n = len(s)
    first, middle, last = [0], range(1, n), [n]
    getslice = s.__getslice__
    return [map(getslice, chain(first, div), chain(div, last))
            for i in range(n) for div in combinations(middle, i)]
            
def sum_to_n(n):
    'Generate the series of +ve integer lists which sum to a +ve integer, n.'
    from operator import sub
    b, mid, e = [0], list(range(1, n)), [n]
    splits = (d for i in range(n) for d in combinations(mid, i)) 
    return (list(map(sub, chain(s, e), chain(b, s))) for s in splits)

def minimal_partition(n,L): 
    h = n/L
    err = n - L*h
    bas = L - err
    j = bas + 1
    if h <> 1:
        j = 1
    return [h+1]*err + [h]*bas, j       

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
        
    partition, j = minimal_partition(n,L)
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
        partition[L-j-k+1:L], j = minimal_partition(s,j+k-1)     

for I in fixed_lex_partitions(7,3):
    print I
for J in fixed_length_partitions(7,3):
    print J
class IteratorTest(unittest.TestCase):
    pass
        
        
