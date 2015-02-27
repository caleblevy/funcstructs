#!/usr/bin/env python
# Copyright (C) 2014-2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.

""" Enumerate every conjugacy class of graphs on N nodes with outdegree one for
every vertex. As far as I know this is original work, and endofunction
structures have not been enumerated anywhere else.

Most of these algorithms were derived by Caleb Levy in February 2014. For more
information contact caleb.levy@berkeley.edu. """


import math
import fractions
import itertools

import numpy as np
from PADS import IntegerPartitions

from . import multiset
from . import rootedtrees
from . import subsequences
from . import necklaces
from . import levypartitions
from . import factorization
from . import compositions
from . import endofunctions
from . import productrange


def chunks(l, n):
    """ Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i+n]


def indent_treestring(tree, second_indent, end):
    """Format a rooted tree string with indents."""
    treestr = str(rootedtrees.unordered_tree(tree))
    treestr_list = [treestr[:end]]
    for s in chunks(treestr[end:], end-second_indent):
        treestr_list.append(' '*second_indent+s)
    return treestr_list


def struct_string(func, cycle_prefix=2, cycle_suffix=2, tree_indent=4, end=78):
    fstrs = []
    fstrs.append('\nFuncstruct:\n')
    cycle_str = ' '*cycle_prefix + 'Cycle(' + ' '*cycle_suffix
    l = len(cycle_str)
    for cycle, count in func.cycles.items():
        fstrs.append(cycle_str+'\n')
        for tree in cycle:
            for t in indent_treestring(tree, tree_indent, end-l):
                fstrs.append(' '*l+t+'\n')
        fstrs.append(' '*(l-cycle_suffix-1)+')'+' * '+str(count)+'\n')
    return ''.join(fstrs)


def _func_to_struct(f):
    cycles = []
    for cycle in f.cycles:
        strand = []
        for el in cycle:
            strand.append(f.attached_tree(el))
        cycles.append(necklaces.Necklace(strand))
    return cycles


class Funcstruct(object):
    __slots__ = ['cycles', 'n']

    def __init__(self, cycles, precounted=None):
        if isinstance(cycles, endofunctions.Endofunction):
            cycles = _func_to_struct(cycles)
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

    def __str__(self):
        return struct_string(self)

    @property
    def degeneracy(self):
        """ The number of equivalent ways of labelling each endofunction with
        unlabelled structure self.

        The size of the conjugacy class of self is n!/self.degeneracy() """
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
            func_tree = tree.labelled_sequence(tree_perm)
            func.extend(func_tree)
            tree_start += l
        # Permute the cyclic nodes to form the cycle decomposition
        cycle_start = 0
        for cycle in cycles:
            node_prev = node = 0
            cycle_len = len(productrange.flatten(cycle))
            for tree in cycle:
                node += len(tree)
                func[cycle_start+node_prev] = cycle_start + (node % cycle_len)
                node_prev += len(tree)
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


def funcstruct_enumerator(n):
    """Enumerate endofunction structures on n elements. Equalivalent to all
    conjugacy classes in TransformationMonoid(n)."""
    for forest in rootedtrees.ForestEnumerator(n):
        for mpart in forest.partitions():
            for struct in productrange.unordered_product(
                mpart,
                necklaces.FixedContentNecklaces
            ):
                yield Funcstruct(struct, n)


def direct_unordered_attachments(t, l):
    """Enumerate the ways of directly attaching t unlabelled free nodes to l
    unlabelled nodes."""
    return levypartitions.fixed_lex_partitions(t+l, l)


def attachment_forests(t, l):
    """Enumerate all ways to make rooted trees from t free nodes and attach
    them to a a cycle of length l."""
    for partition in direct_unordered_attachments(t, l):
        for forest in rootedtrees.PartitionForests(partition):
            for necklace in necklaces.FixedContentNecklaces(forest):
                yield necklace


def component_groups(c, l, m):
    """ Enumerate ways to make rooted trees from c free nodes and attach them
    to a group of m cycles of length l. """
    iterfunc = lambda y: attachment_forests(y-1, l)
    for partition in direct_unordered_attachments(c, m):
        for cycle_group in productrange.unordered_product(partition, iterfunc):
            yield cycle_group


def cycle_type_funcstructs(n, cycle_type):
    """ Enumerate all funcstructs on n nodes corresponding to a give cycle
    type. """
    treenodes = n - sum(cycle_type)
    lengths, multiplicities = cycle_type.split()
    l = len(lengths)
    for composition in compositions.weak_compositions(treenodes, l):
        cycle_groups = []
        for c, l, m in zip(composition, lengths, multiplicities):
            cycle_groups.append(component_groups(c, l, m))
        for bundle in itertools.product(*cycle_groups):
            yield Funcstruct(productrange.flatten(bundle), n)


class EndofunctionStructures(object):
    def __init__(self, node_count, cycle_type=None):
        self.n = node_count
        self.cycle_type = multiset.Multiset(cycle_type)

    def __repr__(self):
        struct_string = self.__class__.__name__+'('+str(self.n)
        if self.cycle_type:
            struct_string += ', '+repr(cycle_type)
        struct_string += ')'
        return struct_string

    def __hash__(self):
        return hash(tuple([self.n, self.cycle_type]))

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.n == other.n and self.cycle_type == other.cycle_type
        return False

    def __ne__(self, other):
        return not self == other

    def __iter__(self):
        if not self.cycle_type:
            return funcstruct_enumerator(self.n)
        else:
            return cycle_type_funcstructs(self.n, self.cycle_type)

    def cardinality(self):
        """Count the number of endofunction structures on n nodes. Iterates
        over the tuple representation of partitions using the formula featured
        in De Bruijn, N.G., "Enumeration of Mapping Patterns", Journal of
        Combinatorial Theory, Volume 12, 1972. See the papers directory for the
        original reference."""
        tot = 0
        for b in levypartitions.tuple_partitions(self.n):
            product_terms = []
            for i in range(1, len(b)):
                s = 0
                for j in factorization.divisors(i):
                    s += j * b[j]
                s **= b[i]
                s *= fractions.Fraction(i, 1)**(-b[i])/math.factorial(b[i])
                product_terms.append(s)
            tot += multiset.prod(product_terms)
        return int(tot)


def partition_funcstructs(n):
    for i in range(1, n+1):
        for partition in IntegerPartitions.partitions(i):
            for struct in EndofunctionStructures(n, partition):
                yield struct
