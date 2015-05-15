"""Algorithms and data structures for endofunction structures: conjugacy
classes of the transformation monoid, represented by directed graphs with nodes
of outdegree one.

Caleb Levy, 2014 and 2015.
"""

from fractions import Fraction
import itertools
from math import factorial

import numpy as np

from PADS import IntegerPartitions

from . import (
    bases,
    compositions,
    endofunctions,
    factorization,
    subsequences,
)
from .multiset import Multiset, unordered_product
from .necklaces import Necklace, FixedContentNecklaces
from .rootedtrees import DominantTree, PartitionForests
from .utils import flatten


def _partitions(n):
    """Wrapper for D Eppstein's partitions returning multisets"""
    for partition in IntegerPartitions.partitions(n):
        yield Multiset(partition)


class Funcstruct(Multiset):
    """ An endofunction structure may be represented as a forest of trees,
    grouped together in multisets corresponding to cycle decompositions of the
    final set (the subset of its domain on which it is invertible). The
    orderings of the trees in the multisets correspond to necklaces whose beads
    are the trees themselves."""

    __slots__ = '__n'

    def __new__(cls, cycles, precounted=None):
        self = super(Funcstruct, cls).__new__(cls, cycles)
        if precounted is not None:
            self.__n = precounted
        else:
            self.__n = len(list(flatten(flatten(self))))
        return self

    def __len__(self):
        """Number of nodes in the structure."""
        return self.__n

    @classmethod
    def from_func(cls, f):
        cycles = []
        for cycle in f.cycles:
            strand = []
            for el in cycle:
                strand.append(DominantTree.from_func(f, el))
            cycles.append(Necklace(strand))
        return cls(cycles)

    @property
    def degeneracy(self):
        """The number of ways to label a graph representing a particular
        endofunction with the given structure."""
        # First the degeneracy from the permutations of arrangements of cycles
        deg = super(Funcstruct, self).degeneracy()
        # Then account for the periodcity of each cycle
        for cycle, mult in self.items():
            cycledeg = cycle.degeneracy()
            # Finally the degeneracy of each rooted tree.
            for tree in cycle:
                cycledeg *= tree.degeneracy()
            deg *= cycledeg ** mult
        return deg

    def func_form(self):
        """Return a representative endofunction defined on range(n)."""
        func = []
        root_node = end_node = 0
        for cycle in self:
            cycle_start = len(func)
            for tree in cycle:
                end_node += len(tree)
                # Form tree function labelled with the acyclic nodes
                func.extend(tree.map_labelling(range(root_node, end_node)))
                # Permute the cyclic nodes to form the cycle decomposition
                func[root_node] = end_node
                root_node = end_node
            func[root_node-len(tree)] = cycle_start
        return endofunctions.rangefunc(func)

    @property
    def imagepath(self):
        """Image path of an endofunction with the same structure."""
        cardinalities = [len(self), 0] + [0]*(len(self)-2)
        for cycle, mult in self.items():
            for tree in cycle:
                for subseq in subsequences.increasing(tree[1:]):
                    for it in subseq[:-1]:
                        cardinalities[subseq[-1]-it+1] -= mult
                    cardinalities[1] -= mult
        return np.cumsum(cardinalities, dtype=object)[1:]


def direct_unordered_attachments(t, l):
    """Enumerate the ways of directly attaching t unlabelled free nodes to l
    unlabelled nodes."""
    return IntegerPartitions.fixed_length_partitions(t+l, l)


def attachment_forests(t, l):
    """Enumerate all ways to make rooted trees from t free nodes and attach
    them to a a cycle of length l."""
    for partition in direct_unordered_attachments(t, l):
        for forest in PartitionForests(partition):
            for necklace in FixedContentNecklaces(forest):
                yield necklace


def component_groups(c, l, m):
    """ Enumerate ways to make rooted trees from c free nodes and attach them
    to a group of m cycles of length l. """
    for partition in direct_unordered_attachments(c, m):
        for cycle_group in unordered_product(
                partition,
                lambda y: attachment_forests(y-1, l)):
            yield cycle_group


def cycle_type_funcstructs(n, cycle_type):
    """ Enumerate all funcstructs on n nodes corresponding to a give cycle
    type. """
    treenodes = n - sum(cycle_type)
    lengths, multiplicities = cycle_type.split()
    for composition in compositions.weak_compositions(treenodes, len(lengths)):
        cycle_groups = []
        for c, l, m in zip(composition, lengths, multiplicities):
            cycle_groups.append(component_groups(c, l, m))
        for bundle in itertools.product(*cycle_groups):
            yield Funcstruct(flatten(bundle), n)


def integer_funcstructs(n):
    """Enumerate endofunction structures on n elements. Equivalent to all
    conjugacy classes in TransformationMonoid(n)."""
    for i in range(1, n+1):
        for partition in _partitions(i):
            for struct in cycle_type_funcstructs(n, partition):
                yield struct


class EndofunctionStructures(bases.Enumerable):
    """Enumerator of endofunction structures consisting of n nodes, optionally
    restricted to a given cycle type."""

    def __init__(self, node_count, cycle_type=None):
        super(EndofunctionStructures, self).__init__(node_count, cycle_type, 0)

    def __iter__(self):
        if not self.partition:
            return integer_funcstructs(self.n)
        else:
            return cycle_type_funcstructs(self.n, self.partition)

    def cardinality(self):
        """Count the number of endofunction structures on n nodes. Iterates
        over the tuple representation of partitions using the formula featured
        in De Bruijn, N.G., "Enumeration of Mapping Patterns", Journal of
        Combinatorial Theory, Volume 12, 1972. See the papers directory for the
        original reference."""
        tot = 0
        for part in _partitions(self.n):
            p = 1
            for i in range(1, self.n+1):
                s = sum(j*part.get(j, 0) for j in factorization.divisors(i))
                b = part.get(i, 0)
                p *= s**b * Fraction(i, 1)**(-b)/factorial(b)
            tot += p
        return int(tot)
