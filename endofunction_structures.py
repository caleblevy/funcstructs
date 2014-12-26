#! /usr/bin/env python
"""endofunction_structures.py
Enumerate every conjugacy class of graphs on N nodes with outdegree one for
every vertex. As far as I know this is original work, and endofunction
structures have not been enumerated anywhere else.

Caleb Levy, February 2014. For more information contact caleb.levy@berkeley.edu.
"""

from rooted_trees import forests, split_set, flatten, mset_degeneracy, tree_degeneracy
from necklaces import necklaces, cycle_degeneracy
from itertools import combinations_with_replacement, product
from sympy.utilities.iterables import multiset_partitions
from math import factorial
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

def tree_to_func(tree, permutation=None):
    """
    Convert a tree into an endofunction list, whose root is by default at zero,
    but can be permuted according a specified permutation.
    """
    n = len(tree)
    if permutation is None:
        permutation = range(n)
    height = max(tree)
    func = range(n)
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
    
def _treeform_of_noncyclic_nodes(function_structure):
    tree_start = 0
    func = []
    for tree in flatten(function_structure):
        l = len(tree)
        func_tree = tree_to_func(tree, permutation=range(tree_start, tree_start+l)) 
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
        
class EndofunctionStructureTest(unittest.TestCase):
    counts = [0, 1, 3, 7, 19, 47, 130, 343, 951, 2615, 7318, 20491, 57903]
    def testTreeToFunc(self):
        tree = [1,2,3,4,4,4,3,4,4,2,3,3,2,3]
        func = [0,0,1,2,2,2,1,6,6,0,9,9,0,12]
        self.assertEqual(func, tree_to_func(tree))
    
    def testFuncstructToFunc(self):
        func_struct = [((1,2,3,),(1,2,2,)),((1,2,),),((1,2,2),(1,),(1,2,2,))]
        func = [3, 0, 1, 0, 3, 3, 6, 6, 11, 8, 8, 12, 8, 12, 12]
        self.assertEqual(func, funcstruct_to_func(func_struct))
    # OEIS A001372
    def testFuncstructCount(self):
        """check rooted trees has the right number of outputs"""
        for n in range(len(self.counts)):
            struct_count = 0
            for struct in funcstructs(n):
                struct_count += 1
            self.assertEqual(self.counts[n], struct_count)
            
    def testFuncstructDegeneracy(self):
        # OEIS A000312
        for n in range(1, len(self.counts)):
            nfac = factorial(n)
            func_count = 0
            for funcstruct in funcstructs(n):
                func_count += nfac/funcstruct_degeneracy(funcstruct)
            self.assertEqual(n**n, func_count)

if __name__ == '__main__':
    unittest.main()

