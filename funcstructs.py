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

Most of these algorithms were derived by Caleb Levy in February 2014. For more
information contact caleb.levy@berkeley.edu.
"""

import unittest
from math import factorial
from fractions import Fraction
from itertools import combinations_with_replacement, product


from sympy.utilities.iterables import multiset_partitions
import numpy as np

from multiset import split_set, mset_degeneracy, prod
from funcimage import imagepath
from nestops import flatten
from rootedtrees import forests, tree_degeneracy, tree_to_func
from monotones import increasing_subsequences
from necklaces import necklaces
from rotation import cycle_degeneracy
from levypartitions import tuple_partitions
from primes import divisors


def multiset_funcstructs(mset):
    """
    Given a multiset of rooted trees, return all endofunction structures whose
    cycles correspond to the multisets.
    """
    mset = [tuple(m) for m in mset]
    beadsets, mults = split_set(mset)
    strands = []
    for I, beads in enumerate(beadsets):
        necklace_sets = list(necklaces(beads))
        strand = list(combinations_with_replacement(necklace_sets, mults[I]))
        strands.append(strand)

    for bundle in product(*strands):
        yield flatten(bundle)


def funcstructs(n):
    """
    An enumeration of endofunction structures on n elements. Equalivalent to
    all conjugacy classes in End(S)
    """
    for forest in forests(n):
        for mset in multiset_partitions(forest):
            for funcstruct in multiset_funcstructs(mset):
                yield funcstruct


def funcstruct_count(n):
    """
    Count the number of endofunction structures on n nodes. Iterates over the
    tuple representation of partitions using the formula featured in
        De Bruijn, N.G., "Enumeration of Mapping Patterns", Journal of
        Combinatorial Theory, Volume 12, 1972.

    See the papers directory for the original reference.
    """
    tot = 0
    for b in tuple_partitions(n):
        product_terms = []
        for I in range(1, len(b)+1):
            s = 0
            for J in divisors(I):
                s += J*b[J-1]
            s **= b[I-1]
            s *= Fraction(I, 1)**(-b[I-1])/factorial(b[I-1])
            product_terms.append(s)
        tot += prod(product_terms)
    return int(tot)


def funcstruct_degeneracy(function_structure):
    """
    The number of equivalent representations of a labelling of an endofunction
    with unlabelled structure funcstruct.

    The size of the conjugacy class of funcstruct is
    n!/funcstruct_degeneracy(funcstruct)
    """
    if not function_structure:
        return 1
    # First the degeneracy from the permutations of arrangements of cycles
    degeneracy = mset_degeneracy(function_structure)
    # Then account for the periodcity of each cycle
    for cycle in function_structure:
        degeneracy *= cycle_degeneracy(cycle)
    # Finally the degeneracy of each rooted tree.
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
        cycle_len = len(flatten(cycle))
        for tree in cycle:
            node_next += len(tree)
            func[cycle_start+node_ind] = cycle_start + (node_next % cycle_len)
            node_ind += len(tree)
        cycle_start += cycle_len
    return func


def funcstruct_imagepath(funcstruct):
    """
    Given an endofunction structure funcstruct, compute the image path directly
    without conversion to a particular endofunction.
    """
    forest = flatten(funcstruct)
    cardinalities = np.array([0]+[0]*(len(flatten(forest))-2), dtype=object)
    for tree in forest:
        cardinalities += 1
        for subseq in increasing_subsequences(tree):
            k = len(subseq) - 1
            k -= 1 if subseq[0] is 1 else 0
            if k > 0:
                # Microoptimization: memoize the calls to range
                cardinalities[:k] += range(k, 0, -1)
    return cardinalities


class EndofunctionStructureTest(unittest.TestCase):

    def testFuncstructToFunc(self):
        func_struct = [
            ((1, 2, 3,), (1, 2, 2)),
            ((1, 2,), ),
            ((1, 2, 2), (1, ), (1, 2, 2,))
        ]

        func = [3, 0, 1, 0, 3, 3, 6, 6, 11, 8, 8, 12, 8, 12, 12]
        self.assertEqual(func, funcstruct_to_func(func_struct))

    def testFuncstructImagepath(self):
        """Check methods for computing structure image paths are equivalent."""
        N = 8
        for n in range(1, N):
            for struct in funcstructs(n):
                im = imagepath(funcstruct_to_func(struct))
                imstruct = funcstruct_imagepath(struct)
                np.testing.assert_array_equal(im, imstruct)

    def testFuncstructCounts(self):
        """OEIS A001372: Number of self-mapping patterns."""
        A001372 = [1, 3, 7, 19, 47, 130, 343, 951, 2615, 7318, 20491, 57903]
        for n, num in enumerate(A001372):
            struct_count = 0
            for struct in funcstructs(n+1):
                struct_count += 1
            self.assertEqual(num, struct_count)
            self.assertEqual(num, funcstruct_count(n+1))

    def testFuncstructDegeneracy(self):
        """OEIS A000312: Number of labeled maps from n points to themselves."""
        N = 8
        for n in range(1, N):
            nfac = factorial(n)
            func_count = 0
            for funcstruct in funcstructs(n):
                func_count += nfac//funcstruct_degeneracy(funcstruct)
            self.assertEqual(n**n, func_count)


if __name__ == '__main__':
    unittest.main()
