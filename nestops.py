#!/usr/bin/env python
# Copyright (C) 2014 Caleb Levy - All Rights Reserved.
# 
# The terms of use, license and copyright information for the code and ideas 
# contained herein are described in the LICENSE file included with this 
# project. For more information please contact me at caleb.levy@berkeley.edu.

import numpy as np
from setops import isiterable
import unittest

def Unpack(PList): # Extract the next level of a rooted tree
    PList = [M for M in PList if isinstance(M,list)]
    UP = []    
    for M in PList:
        for El in M:
            UP.append(El)            
    return UP
    
def ListNestedEls(Tree,d): # List all elements at depth d, representing nodes with further connections as their own trees
    for I in range(d):
        Tree = Unpack(Tree)
    return Tree
        
def Unwind(Tree): # Give all the elements in the nodes of a tree
    S = []
    while Tree:
        M = [I for I in Tree if not isinstance(I,list)]
        for El in M:
            S.append(El)
        Tree = Unpack(Tree)
    return list(set(S))
        
def numels_by_nestdepth(Tree): # Find the level path of a rooted tree, including 1 in the base
    L = []
    L.append(1)
    while Tree:
        L.append(len(Tree))
        Tree = Unpack(Tree)
    return L
    
def get_nested_el(tree, ind):
    # As long as we can still iterate through tree, continue
    if not isiterable(tree):
        raise ValueError('Tree depth exceeded')
    if not isiterable(ind):
        return tree[ind]
    if len(ind) == 1:
        return tree[ind[0]]
    else:
        return get_nested_el(tree[ind[0]], ind[1:])
    
def change_nested_el(tree, ind, el):
    # As long as we can still iterate through tree, continue
    if not isiterable(tree):
        raise ValueError('Tree depth exceeded')
    # Guard against base case of integer index
    if not isiterable(ind):
        tree[ind] = el
    elif len(ind) == 1:
        tree[ind[0]] = el
    else:
        change_nested_el(tree[ind[0]], ind[1:], el)
        
def IImage(f): # Return the inverse image of S under f
    N = len(f)
    S = range(N)
    Im = [None]*N
    for I in range(N):
        Im[I] = [J for J in S if f[J]==I]               
    return Im
    
def nestedform(treefunc):
    n = len(treefunc)
    S = range(n)
    im = IImage(treefunc)
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

class NestedtreeTest(unittest.TestCase):
    funcforms = [
        [0, 0, 1, 2, 3, 4, 2, 0, 7, 8],
        [0, 0, 1, 2, 3, 4, 2, 0, 7, 7],
        [0, 0, 1, 2, 3, 3, 3, 3, 3, 0],
    ]
    nestedforms = [
        [[[[[[]]], []]], [[[]]]],
        [[[[[[]]], []]], [[], []]],
        [[[[[], [], [], [], []]]], []]
    ]
    
    def testTreeform(self):
        for I, tree in enumerate(self.funcforms):
            self.assertEqual(self.nestedforms[I], nestedform(tree))
    

if __name__ == '__main__':
    unittest.main()