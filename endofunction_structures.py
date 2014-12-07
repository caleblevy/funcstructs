#! /usr/bin/env python
"""endofunction_structures.py
Enumerate every conjugacy class of graphs on N nodes with outdegree one for every vertex. As far as I know this is
original work, and endofunction structures have not been enumerated anywhere else.

Caleb Levy, February 2014. For more information contact caleb.levy@berkeley.edu.
"""

from rooted_trees import forests, split_set, unpack, mset_degeneracy, tree_degeneracy
from necklace import necklaces, cycle_degeneracy
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
        el_strands = list(combinations_with_replacement(el_necklaces, multiplicities[ind]))
        necklace_lists.append(el_strands)
    for bundle in product(*necklace_lists):
        function_structure = []
        for item in bundle:
            function_structure.extend(item)
        yield function_structure
    
def endofunction_structures(n):
    """An enumeration of endofunction structures on n elements. Equalivalent to all conjugacy classes in End(S)"""
    for forest in forests(n):
        for mset in multiset_partitions(forest):
            for function_structure in mset_functions(mset):
                yield function_structure

def structure_multiplicity(function_structure):
    if not function_structure:
        return 1
    n = len(unpack(unpack(function_structure)))
    degeneracy = mset_degeneracy(function_structure)
    for cycle in function_structure:
        degeneracy *= cycle_degeneracy(cycle)
    forest = unpack(function_structure)
    for tree in forest:
        degeneracy *= tree_degeneracy(tree)
    return factorial(n)/degeneracy

def tree_to_func(tree, permutation=None):
    """
    Convert a tree into an endofunction list, whose root is by default at zero, but can be permuted according a
    specified permutation.
    """
    n = len(tree)
    if not permutation:
        permutation = range(n)
    height = max(tree)
    func = range(n)
    func[0] = permutation[0]
    height_prev = 1
    grafting_point = [None]*height # Most recent node found at height h. Where to graft the next node to.
    grafting_point[0] = 0
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
    for tree in unpack(function_structure):
        l = len(tree)
        func_tree = tree_to_func(tree, permutation=range(tree_start, tree_start+l))
        func.extend(func_tree)
        tree_start += l
    return func
    
def endofunction_to_func(function_structure):
    """Convert function structure to canonical form by filling in numbers from 0 to n-1 on the cycles and trees."""
    func = _treeform_of_noncyclic_nodes(function_structure)
    cycle_start = 0
    for cycle in function_structure:
        node_ind = node_next = 0
        cycle_len = len(unpack(cycle))
        for tree in cycle:
            node_next += len(tree)
            func[cycle_start + node_ind] = cycle_start + node_next%cycle_len
            node_ind += len(tree)
        cycle_start += cycle_len
    return func
    
def inv(perm):
    """Invert a permutation of integers I=1...n. """
    inverse = [0] * len(perm)
    for i, p in enumerate(perm):
        inverse[p] = i
    return inverse

def first_iterate_multiplicity(function_structure):
    return len(list(set(unpack(unpack(function_structure)))))
    
class EndofunctionTest(unittest.TestCase):
    # OEIS A001372
    counts = [0, 1, 3, 7, 19, 47, 130, 343, 951, 2615, 7318, 20491, 57903, 163898, 466199]
    def testStructures(self):
        """check rooted trees has the right number of outputs"""
        for n in range(len(self.counts)):
            self.assertEqual(self.counts[n],len(list(endofunction_structures(n))))
            
    def testMultipliciy(self):
        # OEIS A000312
        for n in range(1, len(self.counts)):
            self.assertEqual(n**n, sum([structure_multiplicity(func) for func in endofunction_structures(n)]))
            
if __name__ == '__main__':
    tree = [1,2,3,4,4,4, 3,4,4,  2,3,3, 2,3]
    print tree_to_func(tree)
    func_struct = (((1,2,3,),(1,2,2,)),((1,2,),),((1,2,2),(1,),(1,2,2,)))
    print endofunction_to_func(func_struct)
    f = endofunction_to_func(func_struct)
    f = [f[f[I]] for I in range(len(f))]
    print f
    unittest.main()

