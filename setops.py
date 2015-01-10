#!/usr/bin/env python
# Copyright (C) 2014-2015 Caleb Levy - All Rights Reserved.
# 
# The terms of use, license and copyright information for the code and ideas 
# contained herein are described in the LICENSE file included with this 
# project. For more information please contact me at caleb.levy@berkeley.edu.

from functools import reduce
from math import factorial
from operator import mul

prod = lambda iterable: reduce(mul, iterable, 1)
factorial_prod = lambda iterable: prod(factorial(I) for I in iterable)
nCk = lambda n,k: factorial(n)//factorial(k)//factorial(n-k)

def split_set(partition):
    """Splits a multiset into elements and multiplicities."""
    y = list(set(partition))
    d = [partition.count(y[I]) for I in range(len(y))]
    return y, d

def mset_degeneracy(mset):
    y, d = split_set(mset)
    return factorial_prod(d)
    
def get(S):
    """ Get a random element from a set (or any iterable). """
    for x in S:
        return x
    raise ValueError("Cannot retrieve an item from the empty set")
    
def preimage(f):
    """
    Given an endofunction f defined on S=range(len(f)), returns the preimage of
    f. If g=preimage(f), we have 
    
        g[y]=[x for x in S if f[x]==y],
        
    or mathematically:
    
        f^-1(y)={x in S: f(x)=y}. 
    
    Note the particularly close correspondence between python's list
    comprehensions and mathematical set-builder notation.
    """
    S = range(len(f))
    preim = []
    for y in S:
        preim.append([ x for x in S if y == f[x] ])
    return preim
    
    