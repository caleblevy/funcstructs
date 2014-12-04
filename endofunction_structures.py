from rooted_trees import forests, split_set, unpack, mset_degeneracy, tree_degeneracy
from necklace import necklaces, cycle_degeneracy
from itertools import combinations_with_replacement, product
from sympy.utilities.iterables import multiset_partitions
from math import factorial
import unittest
        
def mset_functions(mset):
    mset = [tuple(sorted(m)) for m in mset]
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
    unittest.main()

