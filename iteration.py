from itertools import product, combinations
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

for f in endofunctions(5):
    print f       
class IteratorTest(unittest.TestCase):
    pass
        
        
