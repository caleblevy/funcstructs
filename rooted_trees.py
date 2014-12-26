#!/usr/bin/env python
"""
Copyright (C) 2014 Caleb Levy - All Rights Reserved.

The terms  of non-commercial usage of  this code are simply  providing credit of
some variety,  either in the  typical list of  contributors section of  the code
repository or,  if used for an  academic paper, some contribution  in the paper.
For commercial use, please contact me at caleb.levy@berkeley.edu.
"""
from PADS.IntegerPartitions import partitions
from itertools import combinations_with_replacement, product
from itertools import chain
from math import factorial
from operator import mul
import unittest

prod = lambda iterable: reduce(mul, iterable, 1)
factorial_prod = lambda iterable: prod(factorial(I) for I in iterable)

def successor_tree(L):
    N = len(L)
    p = N-1
    while L[p] == L[1]:
        p -= 1
    q = p-1
    while L[q] >= L[p]:
        q -= 1
    for I in xrange(p,N):
        L[I] = L[I-(p-q)]

def rooted_trees(N):
    """
    Takes an integer N as input and outputs a generator object enumerating all
    isomorphic unlabeled rooted trees on N nodes. 
    
    The basic idea of the algorithm is to represent a tree by its level
    sequence: list each vertice's height above the root, where vertex v+1 is
    connected either to vertex v or the previous node at some lower level.

    Choosing the lexicographically greatest level sequence gives a canonical
    representation for each rooted tree. We start with the tallest rooted tree
    given by T=range(1,N+1) and then go downward, lexicographically, until we
    are flat so that T=[1]+[2]*(N-1).
    
    Algorithm and description provided in:
        T. Beyer and S. M. Hedetniemi. "Constant time generation of rooted
        trees." Siam Journal of Computation, Vol. 9, No. 4. November 1980.
    """
    if N == 0:
        return
    elif N == 1:
        yield (1,)
        return
    elif N == 2:
        yield (1,2)
        return
    L = [I+1 for I in xrange(N)]
    yield L
    while L[1] != L[2]:
        successor_tree(L)
        yield L
            
def split_set(partition):
    """Splits a multiset into elements and multiplicities."""
    y = list(set(partition))
    d = [partition.count(y[I]) for I in xrange(len(y))]
    return y,d

def mset_degeneracy(mset):
    y, d = split_set(mset)
    return factorial_prod(d)
    
def flatten(listOfLists):
    "Flatten one level of nesting"
    return chain.from_iterable(listOfLists)

flatten_to_list = lambda iterable: list(flatten(iterable))

def unsplit_set(y, d):
    """Reverse of split_set."""
    packed_list = [[y[I]]*d[I] for I in xrange(len(y))]
    return flatten(packed_list)
    
def partition_forests(partition):
    y, d = split_set(partition)
    l = len(y)
    trees = [tuple(rooted_trees(I)) for I in y]
    seeds = [combinations_with_replacement(trees[I],d[I]) for I in xrange(l)]
    seeds = [list(seed) for seed in seeds]
    for forest in product(*seeds):
        yield flatten(forest)
        
def forests_complex(n):
    """
    For a given partition of N elements, we can make combinations of trees on
    each of the node groups of that partition. Iterating over all partitions
    gives us all collections of rooted trees on N nodes.
    """
    if n == 0:
        return
    for partition in partitions(n):
        for forest in partition_forests(partition):
            yield forest

def chop(tree):
    """
    Given a tree, returns the collection of subtrees connected to the root node.
    """
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
    """
    Any rooted tree on N+1 nodes can be identically described by a collection
    of rooted trees on N nodes, grafted together at a single root.
    
    To enumerate all collections of rooted trees on N nodes, we reverse the
    principal and enumerate all rooted trees on N+1 nodes, chopping them at the
    base. Much simpler than finding all trees corresponding to a partition.
    """
    if N == 0: return
    for tree in rooted_trees(N+1):
        yield chop(tree)

forests = forests_simple
    
def tree_degeneracy(tree):
    """
    To calculate the degeneracy of a collection of subtrees you start with the
    lowest branches and then work downwards. If a group of nodes can be
    "swapped" on the same level then they are identical for all intents and
    purposes, and therefore we divide by the factorial of their multiplicity.
    The same principal applies to subtrees.

    TODO: A writeup of this with diagrams will be in the notes.
    """
    if not chop(tree):
        return 1
    mul = 1
    for subtree in chop(tree):
        mul *= tree_degeneracy(subtree)
    return mul*mset_degeneracy(chop(tree))

# If run standalone, perform unit tests
class TreeTest(unittest.TestCase):
    counts = [0, 1, 1, 2, 4, 9, 20, 48, 115, 286]
    def testTrees(self):
        """OEIS A000055: number of unlabelled rooted trees on N nodes."""
        for n in range(len(self.counts)):
            self.assertEqual(self.counts[n],len(list(rooted_trees(n))))
    
    def testForests(self):
        """Check len(forests(N))==A000055(N+1)"""
        self.assertEqual(0,len(list(forests_simple(0))))
        self.assertEqual(0,len(list(forests_complex(0))))
        for n in range(1,len(self.counts)-1):
            self.assertEqual(self.counts[n+1],len(list(forests_simple(n))))
            self.assertEqual(self.counts[n+1],len(list(forests_complex(n))))
    
    def testDegeneracy(self):
        """OEIS A000169: n**(n-1) == number of rooted trees on n nodes."""
        self.assertEqual(1,tree_degeneracy(tuple()))
        for n in range(1,len(self.counts)):
            labelled_treecount = 0
            for tree in rooted_trees(n):
                labelled_treecount += factorial(n)/tree_degeneracy(tree)
            self.assertEqual(n**(n-1), labelled_treecount)

if __name__ == '__main__':
    unittest.main()
    
                    
    
