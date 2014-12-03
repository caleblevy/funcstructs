#!/usr/bin/env python
"""
Contains  one main  function:  rooted_trees. Takes  an integer  N  as input  and
outputs a generator object enumerating  all isomorphic unlabeled rooted trees on
N nodes. Consult OEIS A000055 to find len(list(rooted_trees(N))).

Copyright (C) 2014 Caleb Levy - All Rights Reserved.
The terms  of non-commercial usage of  this code are simply  providing credit of
some variety,  either in the  typical list of  contributors section of  the code
repository or,  if used for an  academic paper, some contribution  in the paper.
For commercial use, please contact me at caleb.levy@berkeley.edu.
"""
from eppstein.IntegerPartitions import partitions
from itertools import combinations_with_replacement, product
from collections import Counter
from math import factorial
from operator import mul
import unittest

prod = lambda iterable: reduce(mul, iterable, 1)

def successor(L):
    N = len(L)
    p = N-1
    while L[p] == L[1]:
        p -= 1
    q = p-1
    while L[q] >= L[p]:
        q -= 1
    for I in range(p,N):
        L[I] = L[I-(p-q)]

def rooted_trees(N):
    if N == 0:
        return
    elif N == 1:
        yield (1,)
        return
    elif N == 2:
        yield (1,2)
        return
    L = [I+1 for I in range(N)]
    yield tuple(L)
    while L[1] != L[2]:
        successor(L)
        yield tuple(L)
            
def split_set(partition):
    # splits a multiset into elements and multiplicities
    y = list(set(partition))
    d = [partition.count(y[I]) for I in range(len(y))]
    return y,d
    
def unpack(tree):
    # Takes a list of lists and outputs a list whose elements are those of the sublists.
    packed_list = [I for I in tree if isinstance(I,(tuple,list,set))]
    unpacked = []
    for I in packed_list:
        for el in I:
            unpacked.append(el)
    return unpacked

def unsplit_set(y, d):
    packed_list = [[y[I]]*d[I] for I in range(len(y))]
    return unpack(packed_list)
    
def partition_forests(partition):
    y, d = split_set(partition)
    l = len(y)
    trees = [tuple(rooted_trees(I)) for I in y]
    seeds = [combinations_with_replacement(trees[I],d[I]) for I in range(l)]
    seeds = [list(seed) for seed in seeds]
    for forest in product(*seeds):
        yield tuple(unpack(forest))
        
def forests_complex(n):
    if n == 0:
        return
    for partition in partitions(n):
        for forest in partition_forests(partition):
            yield forest

def chop(tree):
    if not tree or len(tree) == 1:
        return
    tree = tree[1:]
    tree = [t-1 for t in tree]
    forest = []
    subtree = []
    for ind, node in enumerate(tree[:-1]):
        subtree.append(node)
        if tree[ind+1] == 1:
            forest.append(tuple(subtree))
            subtree = []
    if tree[-1] != 1:
        subtree.append(tree[-1])
    else:
        subtree = [tree[-1]]
    forest.append(tuple(subtree))
    return tuple(forest)

def forests_simple(N):
    if N == 0: return
    for tree in rooted_trees(N+1):
        yield chop(tree)

forests = forests_simple

def forest_deg(tree):
    mul = 1
    forest = chop(tree)
    y, d = split_set(forest)
    return prod(factorial(I) for I in d)
    
def deg(tree):
    if not chop(tree):
        return 1
    mul = 1
    for subtree in chop(tree):
        mul *= deg(subtree)
    return mul*forest_deg(tree)

# If run standalone, perform unit tests
class TreeTest(unittest.TestCase):
    # OEIS A000055
    counts = [0, 1, 1, 2, 4, 9, 20, 48, 115, 286]
    def testTrees(self):
        """check rooted trees has the right number of outputs"""
        for n in range(len(self.counts)):
            self.assertEqual(self.counts[n],len(list(rooted_trees(n))))
    
    def testForests(self):
        """Check each forest has the right number of outputs"""
        self.assertEqual(0,len(list(forests_simple(0))))
        self.assertEqual(0,len(list(forests_complex(0))))
        for n in range(1,len(self.counts)-1):
            self.assertEqual(self.counts[n+1],len(list(forests_simple(n))))
            self.assertEqual(self.counts[n+1],len(list(forests_complex(n))))
    
    def testDegeneracy(self):
        """Make sure our degeneracies add up to n^(n-1) trees"""
        self.assertEqual(1,deg(tuple()))
        for n in range(1,len(self.counts)):
            self.assertEqual(n**(n-1),sum([factorial(n)/deg(tree) for tree in rooted_trees(n)]))

if __name__ == '__main__':
    unittest.main()
    
                    
    
