from itertools import product, combinations, chain
from collections import Iterable
from sympy.utilities.iterables import multiset_partitions
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

def partition(iterable, chain=chain, map=map):
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

import time
ts = time.time()
for I in sum_to_n(21):
    pass
tf = time.time()
print tf-ts
ts = time.time()
for I in compositions(21):
    pass
tf = time.time()
print tf - ts
ts = time.time()
for I in sum_to_n(21):
    pass
tf = time.time()
print tf-ts
# print len(list(sum_to_n(17)))
# for f in endofunctions(5):
#     print f
#
# for p in partition([1,1,2,3,3,5]):
#     print p
#
# for q in multiset_partitions([1,1,2,3,3,5]):
#     print q
class IteratorTest(unittest.TestCase):
    pass
        
        
