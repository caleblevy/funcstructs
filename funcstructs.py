#!/usr/bin/env python
# Copyright (C) 2014-2015 Caleb Levy - All Rights Reserved.
# 
# The terms of use, license and copyright information for the code and ideas 
# contained herein are described in the LICENSE file included with this 
# project. For more information please contact me at caleb.levy@berkeley.edu.

"""
Enumerate every conjugacy class of graphs on N nodes with outdegree one for
every vertex. As far as I know this is original work, and endofunction
structures have not been enumerated anywhere else.

Caleb Levy, February 2014. For more information contact caleb.levy@berkeley.edu.
"""

from setops import split_set, flatten, mset_degeneracy, prod
from rootedtrees import forests, tree_degeneracy, tree_to_func
from monotones import increasing_subsequences
from itertools import combinations_with_replacement, product
from sympy.utilities.iterables import multiset_partitions
from necklaces import necklaces, cycle_degeneracy
from math import factorial
import numpy as np
import unittest
        
def mset_functions(mset):
    mset = [tuple(m) for m in mset]
    elems, multiplicities = split_set(mset)
    necklace_lists = []
    for ind, el in enumerate(elems):
        el_necklaces = list(necklaces(el))
        el_strands = list(combinations_with_replacement(el_necklaces, 
                                                        multiplicities[ind]))
        necklace_lists.append(el_strands)
    for bundle in product(*necklace_lists):
        function_structure = []
        for item in bundle:
            function_structure.extend(item)
        yield function_structure
    
def funcstructs(n):
    """
    An enumeration of endofunction structures on n elements. Equalivalent to
    all conjugacy classes in End(S)
    """
    for forest in forests(n):
        for mset in multiset_partitions(forest):
            for function_structure in mset_functions(mset):
                yield function_structure

def funcstruct_degeneracy(function_structure, n=None):
    if not function_structure:
        return 1
    degeneracy = mset_degeneracy(function_structure)
    for cycle in function_structure:
        degeneracy *= cycle_degeneracy(cycle)
    for tree in flatten(function_structure):
        degeneracy *= tree_degeneracy(tree)
    return degeneracy
    
def _treeform_of_noncyclic_nodes(function_structure):
    tree_start = 0
    func = []
    for tree in flatten(function_structure):
        l = len(tree)
        tree_perm = list(range(tree_start, tree_start+l))
        func_tree = tree_to_func(tree, permutation=tree_perm)
        func.extend(func_tree)
        tree_start += l
    return func
    
def funcstruct_to_func(function_structure):
    """
    Convert function structure to canonical form by filling in numbers from 0
    to n-1 on the cycles and trees.
    """
    func = _treeform_of_noncyclic_nodes(function_structure)
    cycle_start = 0
    for cycle in function_structure:
        node_ind = node_next = 0
        cycle_len = len(list(flatten(cycle)))
        for tree in cycle:
            node_next += len(tree)
            func[cycle_start + node_ind] = cycle_start + node_next%cycle_len
            node_ind += len(tree)
        cycle_start += cycle_len
    return func

def funcstruct_imagepath(funcstruct, n=None):
    forest = list(flatten(funcstruct))
    if n is None:
        n = len(list(flatten(forest)))
    cardinalities = np.array([0]+[0]*(n-2), dtype=object)
    for tree in forest:
        cardinalities += 1
        for subseq in increasing_subsequences(tree):
            k = len(subseq) - 1
            k -= 1 if subseq[0] is 1 else 0
            if k > 0:
                # Microoptimization: memoize the calls to range
                cardinalities[:k] += range(k,0,-1)
    return cardinalities

class EndofunctionStructureTest(unittest.TestCase):

    def testFuncstructToFunc(self):
        func_struct = [((1,2,3,),(1,2,2,)),((1,2,),),((1,2,2),(1,),(1,2,2,))]
        func = [3, 0, 1, 0, 3, 3, 6, 6, 11, 8, 8, 12, 8, 12, 12]
        self.assertEqual(func, funcstruct_to_func(func_struct))

    def testFuncstructCount(self):
        """OEIS A001372: Number of self-mapping patterns."""
        A001372 = [0, 1, 3, 7, 19, 47, 130, 343, 951, 2615, 7318, 20491, 57903]
        for n, num in enumerate(A001372):
            struct_count = 0
            for struct in funcstructs(n):
                struct_count += 1
            self.assertEqual(num, struct_count)
            
    def testFuncstructDegeneracy(self):
        """OEIS A000312: Number of labeled maps from n points to themselves."""
        N = 10
        for n in range(1,N):
            nfac = factorial(n)
            func_count = 0
            for funcstruct in funcstructs(n):
                func_count += nfac//funcstruct_degeneracy(funcstruct)
            self.assertEqual(n**n, func_count)

if __name__ == '__main__':
    unittest.main()

