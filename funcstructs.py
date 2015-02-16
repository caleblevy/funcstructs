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

import math
import fractions
import itertools
import unittest

import numpy as np
from PADS import IntegerPartitions

import multiset
import rootedtrees
import subsequences
import necklaces
import levypartitions
import factorization
import compositions
import endofunctions
import productrange


class Funcstruct(object):

    def __init__(self, cycles, precounted=None):
        self.cycles = multiset.Multiset(cycles)
        if precounted is not None:
            self.n = precounted
        else:
            self.n = len(productrange.flatten(productrange.flatten(cycles)))

    def __hash__(self):
        return hash(self.cycles)

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.cycles == other.cycles

    def __ne__(self, other):
        return not self == other

    __lt__ = None

    def __repr__(self):
        return self.__class__.__name__+'('+repr(list(self.cycles))+')'

    @property
    def degeneracy(self):
        """ The number of equivalent representations of a labelling of an
        endofunction with unlabelled structure funcstruct.

        The size of the conjugacy class of funcstruct is
        n!/funcstruct_degeneracy(funcstruct) """
        if not self.cycles:
            return 1
        # First the degeneracy from the permutations of arrangements of cycles
        degeneracy = self.cycles.degeneracy()
        # Then account for the periodcity of each cycle
        for cycle in self.cycles:
            degeneracy *= cycle.degeneracy()
            # Finally the degeneracy of each rooted tree.
            for tree in cycle:
                degeneracy *= tree.degeneracy()
        return degeneracy

    def func_form(self):
        """ Convert function structure to canonical form by filling in numbers
        from 0 to n-1 on the cycles and trees. """
        # Find the tree form of non-cyclic nodes
        cycles = list(self.cycles)
        tree_start = 0
        func = []
        for tree in productrange.flatten(cycles):
            l = len(tree)
            tree_perm = range(tree_start, tree_start+l)
            func_tree = endofunctions.Endofunction.from_tree(tree, permutation=tree_perm)
            func.extend(func_tree)
            tree_start += l
        # Permute the cyclic nodes to form the cycle decomposition
        cycle_start = 0
        for cycle in cycles:
            node_ind = node_next = 0
            cycle_len = len(productrange.flatten(cycle))
            for tree in cycle:
                node_next += len(tree)
                func[cycle_start+node_ind] = cycle_start + (node_next % cycle_len)
                node_ind += len(tree)
            cycle_start += cycle_len
        return endofunctions.Endofunction(func)

    @property
    def imagepath(self):
        """ Given an endofunction structure funcstruct, compute the image path
        directly without conversion to a particular endofunction. """
        cardinalities = np.array([0]+[0]*(self.n-2), dtype=object)
        for tree in productrange.flatten(self.cycles):
            cardinalities += 1
            for subseq in subsequences.increasing_subsequences(tree):
                k = len(subseq) - 1
                k -= 1 if subseq[0] is 1 else 0
                if k > 0:
                    # Microoptimization: memoize the calls to range
                    cardinalities[:k] += range(k, 0, -1)
        return cardinalities

    @classmethod
    def from_func(cls, f):
        struct = []
        for cycle in f.cycles:
            strand = []
            for el in cycle:
                strand.append(rootedtrees.DominantTree.attached_tree(f, el))
            struct.append(necklaces.Necklace(strand))
        return cls(struct)


class FuncstructEnumerator(object):
    def __init__(self, node_count):
        self.n = node_count

    def __repr__(self):
        return type(self).__name__+'('+str(self.n)+')'

    def __hash__(self):
        return hash(self.n)

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.n == other.n
        return False

    def __ne__(self, other):
        return not self == other

    def __iter__(self):
        """An enumeration of endofunction structures on n elements.
        Equalivalent to all conjugacy classes in End(S)."""
        for forest in rootedtrees.ForestEnumerator(self.n):
            for mpart in forest.partitions():
                for struct in productrange.unordered_product(mpart, necklaces.NecklaceGroup):
                    yield Funcstruct(struct)

    def cardinality(self):
        """Count the number of endofunction structures on n nodes. Iterates
        over the tuple representation of partitions using the formula featured
        in De Bruijn, N.G., "Enumeration of Mapping Patterns", Journal of
        Combinatorial Theory, Volume 12, 1972. See the papers directory for the
        original reference."""
        tot = 0
        for b in levypartitions.tuple_partitions(self.n):
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

    def __len__(self):
        return self.cardinality()


def direct_unordered_attachments(t, l):
    """Enumerate the ways of directly attaching t unlabelled free nodes to l
    unlabelled nodes."""
    return levypartitions.fixed_lex_partitions(t+l, l)


def attachment_forests(t, l):
    """Enumerate all ways to make rooted trees from t free nodes and attach
    them to a a cycle of length l."""
    for partition in direct_unordered_attachments(t, l):
        for forest in rootedtrees.PartitionForests(partition):
            for necklace in necklaces.NecklaceGroup(forest):
                yield necklace


def component_groups(c, l, m):
    """Enumerate ways to make rooted trees from c free nodes and attach them to
    a group of m cycles of length l."""
    # c number of free tree nodes, l length of cycle, m number of cycles
    iterfunc = lambda y: attachment_forests(y-1, l)
    for partition in direct_unordered_attachments(c, m):
        for cycle_group in productrange.unordered_product(partition, iterfunc):
            yield cycle_group


class CycleTypeFuncstructs(object):

    def __init__(self, node_count, cycle_type):
        self.n = node_count
        self.cycle_type = multiset.Multiset(cycle_type)

    def __iter__(self):
        treenodes = self.n - sum(self.cycle_type)
        lengths, multiplicities = self.cycle_type.split()
        l = len(lengths)
        for composition in compositions.weak_compositions(treenodes, l):
            cycle_groups = []
            for c, l, m in zip(composition, lengths, multiplicities):
                cycle_groups.append(component_groups(c, l, m))
            for bundle in itertools.product(*cycle_groups):
                yield Funcstruct(productrange.flatten(bundle))


def partition_funcstructs(n):
    for i in range(1, n+1):
        for partition in IntegerPartitions.partitions(i):
            for struct in CycleTypeFuncstructs(n, partition):
                yield struct


class FuncstructTests(unittest.TestCase):

    mult_structs = [list(FuncstructEnumerator(i)) for i in range(1, 13)]
    part_structs = [list(partition_funcstructs(i)) for i in range(1, 13)]

    def testFuncstructToFunc(self):
        Necklace = necklaces.Necklace
        Tree = rootedtrees.DominantTree
        struct = Funcstruct([
            Necklace([Tree([1, 2, 3]), Tree([1, 2, 2])]),
            Necklace([Tree([1, 2])]),
            Necklace([Tree([1, 2, 2]), Tree([1]), Tree([1, 2, 2])])
        ])
        self.assertEqual(struct, Funcstruct.from_func(struct.func_form()))

    def testFuncstructImagepath(self):
        """Check methods for computing structure image paths are equivalent."""
        for i in range(8):
            for ms, ps in zip(self.mult_structs[i], self.part_structs[i]):
                mim = endofunctions.Endofunction(ms.func_form()).imagepath
                pim = endofunctions.Endofunction(ps.func_form()).imagepath
                msim = ms.imagepath
                psim = ps.imagepath
                np.testing.assert_array_equal(mim, msim)
                np.testing.assert_array_equal(pim, psim)

    def testFuncstructCounts(self):
        """OEIS A001372: Number of self-mapping patterns."""
        A001372 = [1, 3, 7, 19, 47, 130, 343, 951, 2615, 7318, 20491, 57903]
        for i, count in enumerate(A001372):
            self.assertEqual(count, len(set(self.mult_structs[i])))
            self.assertEqual(count, len(set(self.part_structs[i])))
            self.assertEqual(count, len(FuncstructEnumerator(i+1)))

    def testFuncstructDegeneracy(self):
        """OEIS A000312: Number of labeled maps from n points to themselves."""
        for i in range(1, 8):
            fac = math.factorial(i)
            func_mult_count = func_part_count = 0
            for ms, ps in zip(self.mult_structs[i-1], self.part_structs[i-1]):
                func_mult_count += fac//ms.degeneracy
                func_part_count += fac//ps.degeneracy
            self.assertEqual(i**i, func_mult_count)
            self.assertEqual(i**i, func_part_count)

    def test_repr(self):
        from necklaces import Necklace
        from rootedtrees import DominantTree

        struct = Funcstruct.from_func(endofunctions.randfunc(30))
        self.assertEqual(struct, eval(repr(struct)))
        node_counts = [3, 5, 10, 50]
        for n in node_counts:
            structs = FuncstructEnumerator(n)
            self.assertEqual(structs, eval(repr(structs)))


if __name__ == '__main__':
    unittest.main()
