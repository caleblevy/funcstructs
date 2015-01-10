#!/usr/bin/env python
# Copyright (C) 2014-2015 Caleb Levy - All Rights Reserved.
# 
# The terms of use, license and copyright information for the code and ideas 
# contained herein are described in the LICENSE file included with this 
# project. For more information please contact me at caleb.levy@berkeley.edu.

"""
A rooted tree is a connected digraph with a single cycle such that every node's
outdegree and every cycle's length is exactly one. Alternatively, it is a tree
with a designated "root" node, where every path ends with the root. They are
equivalent to filesystems consisting entirely of folders with no symbolic
links. An unlabelled rooted tree is the equivalence class of a given directory
where folders in each subdirectory may be rearranged in any desired order
(alphabetical, reverse-alphabetical, date added, or any other permutation). A
forest is any collection of rooted trees.

Any endofunction structure may be represented as a forest of trees, grouped
together in multisets corresponding to cycle decompositions of the final set
(the subset of its domain on which it is invertible). The orderings of the
trees in the multisets correspond to necklaces whose beads are the trees
themselves.
"""
from setops import mset_degeneracy, split_set, preimage
from nestops import flatten, get_nested_el, change_nested_el
from itertools import combinations_with_replacement, product
from PADS.IntegerPartitions import partitions
from math import factorial
import unittest

def successor_tree(L):
    """Given a tree L, returns the successor."""
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
        yield [1,]
        return
    elif N == 2:
        yield [1,2]
        return
    L = [I+1 for I in range(N)]
    yield L
    while L[1] != L[2]:
        successor_tree(L)
        yield L
    
tree_tuples = lambda n: (tuple(tree) for tree in rooted_trees(n))


def partition_forests(partition):
    y, d = split_set(partition)
    l = len(y)
    trees = [tree_tuples(I) for I in y]
    pre_seed = [combinations_with_replacement(trees[I],d[I]) for I in range(l)]
    seeds = [list(seed) for seed in pre_seed]
    for forest in product(*seeds):
        yield tuple(flatten(forest))
        
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

def subtrees(tree):
    """
    Given a tree, returns the collection of subtrees connected to the root node.
    """
    if not tree or len(tree) == 1:
        return
    tree = [t-1 for t in tree[1:]]
    subtree = []
    for ind, node in enumerate(tree[:-1]):
        subtree.append(node)
        if tree[ind+1] == 1:
            yield subtree
            subtree = []
    if tree[-1] != 1:
        subtree.append(tree[-1])
    else:
        subtree = [tree[-1]]
    yield subtree

def chop(tree):
    return tuple(tuple(subtree) for subtree in subtrees(tree))
    
    
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
    lowest branches and then work upwards. If a group of identical subbranches
    are connected to the same node, we multiply the degeneracy of the tree by
    the factorial of the multiplicity of these subbranches to account for their
    distinct orderings. The same principal applies to subtrees.

    TODO: A writeup of this with diagrams will be in the notes.
    """
    if not chop(tree):
        return 1
    degeneracy = 1
    for subtree in chop(tree):
        degeneracy *= tree_degeneracy(subtree)
    return degeneracy*mset_degeneracy(chop(tree))
    

def tree_to_func(tree, permutation=None):
    """
    Convert a tree into an endofunction list, whose root is by default at zero,
    but can be permuted according a specified permutation.
    """
    n = len(tree)
    if permutation is None:
        permutation = list(range(n))
    height = max(tree)
    func = [0]*n
    func[0] = permutation[0]
    height_prev = 1
    # Most recent node found at height h. Where to graft the next node to.
    grafting_point = [0]*height 
    for node, height in enumerate(tree[1:]):
        if height > height_prev:
            func[node+1] = permutation[grafting_point[height_prev-1]]
            height_prev += 1
        else:
            func[node+1] = permutation[grafting_point[height-2]]
            height_prev = height
        grafting_point[height-1] = node+1
    return func


def treefunc_to_brackets(treefunc):
    n = len(treefunc)
    S = range(n)
    im = preimage(treefunc)
    fix = [I for I in S if treefunc[I]==I]
    
    assert len(fix) == 1 # The tree better be rooted, or we will have an infinite loop
    
    fix = fix[0]
    tree = im[fix]
    tree.remove(fix)
    
    indset = [[I] for I in range(len(tree))]
    
    while indset:
        nextinds = []
        for ind in indset:
            el = get_nested_el(tree, ind)
            for I in range(len(im[el])):
                indn = ind[:]
                indn.append(I)
                nextinds.append(indn)
            
            change_nested_el(tree, ind, im[el])
                
        indset = nextinds
        
    return tree

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
            self.assertEqual(self.counts[n+1],len(set(forests_simple(n))))
            self.assertEqual(self.counts[n+1],len(set(forests_complex(n))))
    
    def testDegeneracy(self):
        """OEIS A000169: n**(n-1) == number of rooted trees on n nodes."""
        self.assertEqual(1,tree_degeneracy(tuple()))
        for n in range(1,len(self.counts)):
            labelled_treecount = 0
            for tree in rooted_trees(n):
                labelled_treecount += factorial(n)//tree_degeneracy(tree)
            self.assertEqual(n**(n-1), labelled_treecount)
            
    def testTreeToFunc(self):
        tree = [1,2,3,4,4,4,3,4,4,2,3,3,2,3]
        func = [0,0,1,2,2,2,1,6,6,0,9,9,0,12]
        self.assertEqual(func, tree_to_func(tree))
    
    
    def testTreeform(self):
        funcforms = [
            [0, 0, 1, 2, 3, 4, 2, 0, 7, 8],
            [0, 0, 1, 2, 3, 4, 2, 0, 7, 7],
            [0, 0, 1, 2, 3, 3, 3, 3, 3, 0],
        ]
        
        nestedforms = (
            [[[[[[]]], []]], [[[]]]],
            [[[[[[]]], []]], [[], []]],
            [[[[[], [], [], [], []]]], []]
        )
        
        for I, tree in enumerate(funcforms):
            self.assertEqual(nestedforms[I], treefunc_to_brackets(tree))


if __name__ == '__main__':
    unittest.main()
