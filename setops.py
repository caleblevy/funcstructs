#!/usr/bin/env python
# Copyright (C) 2014-2015 Caleb Levy - All Rights Reserved.
# 
# The terms of use, license and copyright information for the code and ideas 
# contained herein are described in the LICENSE file included with this 
# project. For more information please contact me at caleb.levy@berkeley.edu.

from functools import reduce
from itertools import chain
from math import factorial
from operator import mul

prod = lambda iterable: reduce(mul, iterable, 1)
factorial_prod = lambda iterable: prod(factorial(I) for I in iterable)

isiterable = lambda obj: hasattr(obj, '__iter__')

def split_set(partition):
    """Splits a multiset into elements and multiplicities."""
    y = list(set(partition))
    d = [partition.count(y[I]) for I in range(len(y))]
    return y, d

def mset_degeneracy(mset):
    y, d = split_set(mset)
    return factorial_prod(d)
    
def flatten(listOfLists):
    "Flatten one level of nesting"
    return chain.from_iterable(listOfLists)
    
flatten_to_list = lambda iterable: list(flatten(iterable))
    
def unsplit_set(y, d):
    """Reverse of split_set."""
    packed_list = [[y[I]]*d[I] for I in range(len(y))]
    return flatten_to_list(packed_list)
    
    

