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
import math
import fractions
import itertools

import numpy as np

import multiset
import nestops
import rootedtrees
import subsequences
import necklaces
import rotation
import levypartitions
import factorization
import iterate


def multiset_funcstructs(mset):
    """
    Given a multiset of rooted trees, return all endofunction structures whose
    cycles correspond to the multisets.
    """
    mset = [tuple(m) for m in mset]
    beadsets, mults = multiset.Multiset(mset).split()
    strands = []
    for mult, beads in zip(mults, beadsets):
        necklace_set = necklaces.necklaces(beads)
        strand = itertools.combinations_with_replacement(necklace_set, mult)
        strands.append(strand)

    for bundle in itertools.product(*strands):
        yield nestops.flatten(bundle)


def funcstructs(n):
    """
    An enumeration of endofunction structures on n elements. Equalivalent to
    all conjugacy classes in End(S)
    """
    for forest in rootedtrees.forests(n):
        for mpart in forest.partitions():
            for funcstruct in multiset_funcstructs(mpart):
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
    for b in levypartitions.tuple_partitions(n):
        product_terms = []
        for I in range(1, len(b)+1):
            s = 0
            for J in factorization.divisors(I):
                s += J*b[J-1]
            s **= b[I-1]
            s *= fractions.Fraction(I, 1)**(-b[I-1])/math.factorial(b[I-1])
            product_terms.append(s)
        tot += multiset.prod(product_terms)
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
    degeneracy = multiset.Multiset(function_structure).degeneracy()
    # Then account for the periodcity of each cycle
    for cycle in function_structure:
        degeneracy *= rotation.cycle_degeneracy(cycle)
    # Finally the degeneracy of each rooted tree.
    for tree in nestops.flatten(function_structure):
        degeneracy *= tree.degeneracy()
    return degeneracy


def _treeform_of_noncyclic_nodes(function_structure):
    tree_start = 0
    func = []
    for tree in nestops.flatten(function_structure):
        l = len(tree)
        tree_perm = range(tree_start, tree_start+l)
        func_tree = tree.func_form(permutation=tree_perm)
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
        cycle_len = len(nestops.flatten(cycle))
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
    forest = nestops.flatten(funcstruct)
    cardinalities = np.array(
        [0]+[0]*(len(nestops.flatten(forest))-2), dtype=object
    )
    for tree in forest:
        cardinalities += 1
        for subseq in subsequences.increasing_subsequences(tree):
            k = len(subseq) - 1
            k -= 1 if subseq[0] is 1 else 0
            if k > 0:
                # Microoptimization: memoize the calls to range
                cardinalities[:k] += range(k, 0, -1)
    return cardinalities


class EndofunctionStructureTest(unittest.TestCase):

    def testFuncstructToFunc(self):
        func_struct = [
            (rootedtrees.RootedTree([1, 2, 3]),
                rootedtrees.RootedTree([1, 2, 2])),
            (rootedtrees.RootedTree([1, 2]), ),
            (rootedtrees.RootedTree([1, 2, 2]),
                rootedtrees.RootedTree([1]), rootedtrees.RootedTree([1, 2, 2]))
        ]
        func = [3, 0, 1, 0, 3, 3, 6, 6, 11, 8, 8, 12, 8, 12, 12]
        self.assertEqual(func, funcstruct_to_func(func_struct))

    def testFuncstructImagepath(self):
        """Check methods for computing structure image paths are equivalent."""
        N = 8
        for n in range(1, N):
            for struct in funcstructs(n):
                im = iterate.imagepath(funcstruct_to_func(struct))
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
            nfac = math.factorial(n)
            func_count = 0
            for funcstruct in funcstructs(n):
                func_count += nfac//funcstruct_degeneracy(funcstruct)
            self.assertEqual(n**n, func_count)


if __name__ == '__main__':
    unittest.main()
