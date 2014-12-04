from rooted_trees import forests, split_set
from necklace import necklaces
from itertools import combinations_with_replacement, product
from sympy.utilities.iterables import multiset_partitions

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
        for ind, item in enumerate(bundle):
            if multiplicities[ind] > 1:
                function_structure.extend(item)
            else:
                function_structure.append(item)
        yield function_structure

def endofunction_structures(n):
    for forest in forests(n):
        for mset in multiset_partitions(forest):
            for function in mset_functions(mset):
                yield function
            
            

if __name__ == '__main__':
    for I in endofunction_structures(5):
        print I
    for I in range(3,14):
        print str(I)+':',len(list(endofunction_structures(I)))