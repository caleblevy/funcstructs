"""Representations and enumerations of endofunction structures.

Caleb Levy, 2014-2015.
"""

from fractions import Fraction
from itertools import chain, product
from math import factorial

from PADS import IntegerPartitions

from funcstructs import compat

from funcstructs.bases import Enumerable
from funcstructs.utils import compositions, factorization, subsequences

from .functions import rangefunc
from .multiset import Multiset, unordered_product
from .necklaces import Necklace, FixedContentNecklaces
from .rootedtrees import _levels_from_preim, DominantTree, PartitionForests


__all__ = ("Funcstruct", "EndofunctionStructures")


def _ispartition(partition):
    """Returns True if given a Multiset of positive integers."""
    return all(isinstance(k, int) and k > 0 for k in partition.keys())


def _partitions(n):
    """Wrapper for D Eppstein's partitions returning multisets"""
    for partition in IntegerPartitions.partitions(n):
        yield Multiset(partition)


class Funcstruct(Multiset):
    """An endofunction structure.

    Intuitively, endofunction structures result from removing the
    labels from a function's graph (where each node x connects to f(x)).

    In mathematical parlance, they are conjugacy classes of
    transformation monoids. Given any two Endofunction objects f and g,
    it follows that Funcstruct(f) == Funcstruct(g) if and only if there
    exists a Bijection b such that f == b.conj(g).

    Funcstruct graphs are directed pseudoforests: Multisets of cycles
    (represented by Necklace objects) whose elements are unlabelled and
    unordered rooted trees (represented by DominantTree objects).

    For example:

        (b)   (c)                  O       O
         \     /                    \     /
          \   /           ==>        \   /
           \ /                        \ /
           (a)                         O

    Corresponds to:

        Endofunction({             Funcstruct.from_cycles([
            "a": "a",                Necklace([
            "b": "a",     ==>          DominantTree([0, 1, 1])
            "c": "a"                 ])
        })                         ])
    """

    __slots__ = ()

    def __new__(cls, f):
        cycles = []
        treenodes = f.acyclic_ancestors()
        for cycle in f.cycles():
            trees = []
            for x in cycle:
                # Use DominantTree instead of RootedTree to avoid hitting
                # python's recursion limit.
                trees.append(DominantTree(_levels_from_preim(treenodes, x)))
            cycles.append(Necklace(trees))
        return super(Funcstruct, cls).__new__(cls, cycles)

    @classmethod
    def _from_cycles(cls, cycles):
        return super(Funcstruct, cls).__new__(cls, cycles)

    def __repr__(self):
        return super(Funcstruct, self).__repr__().replace(
            self.__class__.__name__, self.__class__.__name__+"._from_cycles")

    def __len__(self):
        """Number of nodes in the structure."""
        node_count = 0
        for cycle, mult in self.items():
            node_count += mult * sum(map(len, cycle))
        return node_count

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
        return rangefunc(func)

    def imagepath(self):
        """Image path of an endofunction with the same structure."""
        cardinalities = [len(self), 0] + [0]*(len(self)-2)
        for cycle, mult in self.items():
            for tree in cycle:
                for subseq in subsequences.increasing(tree[1:]):
                    for it in subseq[:-1]:
                        cardinalities[subseq[-1]-it+1] -= mult
                    cardinalities[1] -= mult
        return tuple(compat.accumulate(cardinalities))[1:]


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
    """Enumerate all Funcstructs with the given node count and cycle type."""
    treenodes = n - sum(cycle_type)
    lengths, multiplicities = cycle_type.split()
    for composition in compositions.weak_compositions(treenodes, len(lengths)):
        cycle_groups = []
        for c, l, m in zip(composition, lengths, multiplicities):
            cycle_groups.append(component_groups(c, l, m))
        for bundle in product(*cycle_groups):
            yield Funcstruct._from_cycles(chain(*bundle))


def integer_funcstructs(n):
    """Enumerate endofunction structures on n elements. Equivalent to all
    conjugacy classes in TransformationMonoid(n)."""
    for i in range(1, n+1):
        for partition in _partitions(i):
            for struct in cycle_type_funcstructs(n, partition):
                yield struct


class EndofunctionStructures(Enumerable):
    """Enumerator of endofunction structures consisting of n nodes,
    optionally restricted to a given cycle type. The following invarient
    holds for any n:

    >>> mapping_types = set(map(Funcstruct, TransformationMonoid(n)))
    >>> set(EndofunctionStructures(n)) == mapping_types
    True
    """

    def __init__(self, n, cycle_type=None):
        if n < 0:
            raise ValueError("Cannot defined funcstructs on %s nodes" % n)
        if cycle_type is not None:
            cycle_type = Multiset(cycle_type)
            if not _ispartition(cycle_type):
                raise TypeError("A cycle type must be an integer partition")
        self.n = n
        self.cycle_type = cycle_type

    def __iter__(self):
        if self.cycle_type is None:
            return integer_funcstructs(self.n)
        else:
            return cycle_type_funcstructs(self.n, self.cycle_type)

    def cardinality(self):
        """Count the number of endofunction structures on n nodes.

        Based on De Bruijn, N.G., "Enumeration of Mapping Patterns",
        Journal of Combinatorial Theory, Volume 12, 1972. See the papers
        directory for the original reference."""
        tot = 0
        for part in _partitions(self.n):
            p = 1
            for i in range(1, self.n+1):
                s = sum(j*part.get(j, 0) for j in factorization.divisors(i))
                b = part.get(i, 0)
                p *= s**b * Fraction(i, 1)**(-b)/factorial(b)
            tot += p
        return int(tot)
