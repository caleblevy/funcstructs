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
from .rootedtrees import _levels_from_preim, DominantSequence, TreeEnumerator


__all__ = ("Funcstruct", "EndofunctionStructures")


class Funcstruct(Multiset):
    """An endofunction structure.

    Intuitively, endofunction structures result from removing the
    labels from a function's graph (where each node x connects to f(x)).

    For example:

        (b)   (c)                  O       O
         \     /                    \     /
          \   /           ==>        \   /
           \ /                        \ /
           (a)                         O

    In mathematical parlance, they are conjugacy classes of
    transformation monoids. Given any two Endofunction objects f and g,
    it follows that Funcstruct(f) == Funcstruct(g) if and only if there
    exists a Bijection b such that f == b.conj(g).

    Funcstruct graphs are directed pseudoforests: Multisets of cycles
    (represented by Necklace objects) whose elements are unlabelled and
    unordered rooted trees (represented by DominantSequence objects).
    """

    __slots__ = ()

    def __new__(cls, f):
        cycles = []
        treenodes = f.acyclic_ancestors()
        for cycle in f.cycles():
            trees = []
            for x in cycle:
                # Use DominantSequence instead of RootedTree to avoid hitting
                # python's recursion limit.
                trees.append(
                    DominantSequence(_levels_from_preim(treenodes, x)))
            cycles.append(Necklace(trees))
        return super(Funcstruct, cls).__new__(cls, cycles)

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self.func_form())

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


def _ispartition(partition):
    """Returns True if given a Multiset of positive integers."""
    return all(isinstance(k, int) and k > 0 for k in partition.keys())


def _partitions(n):
    """Wrapper for D Eppstein's partitions returning multisets"""
    for partition in IntegerPartitions.partitions(n):
        yield Multiset(partition)


# The following algorithm for enumerating conjugacy classes of
# endofunctions was derived and implemented by Caleb C. Levy, from
# 2014 to 2015. To the best of his knowledge, this algorithm is novel.


# Enumerating Endofunction Structures with a Fixed Number of Nodes
# ================================================================
# We use the following tools as black boxes: (TODO: link to their modules)
# - Enumerator of every forest with a fixed (multi)set of tree sizes
# - Enumerator of every necklace with a fixed (multi)set of beads
# - Enumerator of weak compositions n into k parts
# - Enumerator of partitions of n (into k parts)
# - Enumerator of a(n unordered) cartesian product of arbitrary sets
#
# Please note that NONE of the above are trivial to implement, but we do
# not discuss them further here.
#
#
# "Groups of Forests" vs "Cycles with Trees"
# ------------------------------------------
# Ignoring their mathematical properties, endofunction structures are simply
# (directed)* pseudoforests (https://en.wikipedia.org/wiki/Pseudoforest).
# They may be viewed equivalently as either (1) forests grouped together in
# cycles, or as (2) cycles with rooted trees attached to them. For the
# purposes of this algorithm we emphasize (2), although this module once
# featured an enumerator based on (1).
#
# In the old algorithm, we simply enumerated all forests on a fixed
# number of nodes, grouped them together in multiset partitions, and
# generated unordered cartesian products of the Necklaces whose elements
# were from the multisets.
#
# This might have been more straightforward if enumerating multiset
# partitions were not so difficult. Sympy is the the only library I am
# aware of with such a function (in python, anyway), and at over 1000
# lines, it exceeds the combined complexity of every other part the
# algorithm!
#
# So using (1) actually adds substantial complexity to the total process.
# Adding a sympy dependency also greatly increased import time,
# restricted compatibility with other python implementations, and the
# implementation slower (by ~4x) at the set sizes we are interested in.
#
# * They need not be directed if we distinguish between psudoforest components
#   which are mirrors, but NOT rotations, of each other. This distinction
#   is important but subtle. (TODO: Add example with brute force conjugating)
#
# Cycle Types
# -----------
# Viewpoint (2) is suggestive of looking at transformation monoids as
# generalizations of the symmetric group. We define a node of an
# endofunction as "cyclic" if it is in a cycle (or the root of a tree).
# The remaining nodes are called "tree" nodes.
#
# The "cycle type" of an endofunction is the cycle type of the permutation
# obtained by removing all of its tree nodes. This may be any partition
# of an integer between 1 and the number of nodes.
#
# The next step is to enumerate the endofunction structures of a fixed
# cycle type and number of tree nodes.


def integer_funcstructs(n):
    """Enumerate endofunction structures on n elements. Equivalent to
    all conjugacy classes in TransformationMonoid(n)."""
    for i in range(1, n+1):
        # TODO: partition micro-benchmarks using groupby vs Multiset.
        for partition in _partitions(i):
            for struct in cycle_type_funcstructs(n, partition):
                yield struct


# Endofunction Structures with a Given Cycle Type
# -----------------------------------------------
# Our next task is two-fold: (a) forming trees with the remaining tree nodes
# and (b) enumerating ways of attaching them to the partition of cycles.
# Problem (a) is solved via our black box, so we focus mainly on (b).
#
# The underlying permutation may be divided into "components": groups of
# cycles with the same length. No matter how the tree nodes are connected
# to each other or to the cyclic nodes, any endofunctions with distinct
# allocations of tree nodes will have different structure.
# (TODO: find which step in the twelve-fold path this is).
#
# Let n be the total number of nodes and k be the number of cyclic nodes.
# If we impose an (arbitrary) ordering on the components, these allocations
# will correspond to weak compositions of n into k parts (components).
#
# A "component group" is a component with rooted trees attached to it.
# Once we have a mechanism to enumerate component groups formable from
# a component and a set of tree nodes, we take the cartesian product
# of each set of component groups to get the endofunction structures
# corresponding to an weak composition of tree nodes.
#
# The next section describes such a mechanism.

def cycle_type_funcstructs(n, cycle_type):
    """Enumerate all Funcstructs with the given node count and cycle type."""
    treenodes = n - sum(cycle_type)
    lengths, mults = zip(*cycle_type.items()) if cycle_type else ((), ())
    for composition in compositions.weak_compositions(treenodes, len(lengths)):
        cycle_groups = []
        for c, l, m in zip(composition, lengths, mults):
            cycle_groups.append(component_groups(c, l, m))
        for bundle in product(*cycle_groups):
            yield Multiset.__new__(Funcstruct, chain(*bundle))


# 12-Fold Path: Item #10
# ----------------------
# Consider a component with m cycles of length l. We wish enumerate
# every component group we can form by connecting t tree nodes to themselves
# or the cycles.
#
# Our first step for enumerating component groups is allocating the tree
# nodes amongst the cycles of the component. Prior to attaching the
# trees, neither the cycles (bins) nor the nodes (balls) are
# distinguishable (labelled) from each other, thus the problem reduces
# directly to distributing t unlabelled balls into m unlabelled boxes.
#
# This is problem #10 in the "Twelve-Fold Path" (see the references), and
# it is solved enumerating partitions of t into at most m parts, or
# equivalently, partitions of t+m into exactly m parts. The latter
# proves more convenient for our purposes.


def direct_unordered_attachments(t, m):
    """Enumerate the ways of directly attaching t unlabelled free nodes to l
    unlabelled nodes."""
    return IntegerPartitions.fixed_length_partitions(t+m, m)


# Component Groups
# ----------------
# We refer to any way of attaching tree nodes to themselves or a
# cycle as an attachment. Suppose we have a way to enumerate
# attachments of t nodes to a cycle of length l.
#
# We then take the unordered cartesian product of these sets of
# attachments to generate the component groups for a given allocation of
# nodes. The "unordered"-ness of the product is an important and subtle
# detail which only shows up when dealing with three or more cycles.
# (TODO: fille this detail in, establish min node bound).
#
# All that remains is to enumerate attachments of t nodes onto a cycle
# of length l.

def component_groups(t, l, m):
    """Enumerate ways to make rooted trees from t free nodes and attach
    them to a group of m cycles of length l.
    """
    for partition in direct_unordered_attachments(t, m):
        for cycle_group in unordered_product(
                partition,  # TODO: remember how that "y-1" works
                lambda y: attachment_forests(y-1, l)):
            yield cycle_group


# Attachments
# -----------
# To find the attachments, we enumerate every forest with precisely as
# many trees as there are elements in the cycle, then enumerate the
# necklaces whose elements are the trees of the forest.

def attachment_forests(t, l):
    """Enumerate all ways to make rooted trees from t free nodes and attach
    them to a a cycle of length l."""
    for partition in direct_unordered_attachments(t, l):
        # TODO: get rid of duplicate Multiset madness here
        for forest in unordered_product(partition, TreeEnumerator):
            for necklace in FixedContentNecklaces(forest):
                yield necklace


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
