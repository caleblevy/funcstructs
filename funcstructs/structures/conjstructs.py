"""Representations and enumerations of endofunction structures.

Caleb Levy, 2014-2015.
"""

from collections import defaultdict
from fractions import Fraction
from itertools import chain, product, combinations_with_replacement
from math import factorial

from PADS import IntegerPartitions

from funcstructs import compat

from funcstructs.bases import Enumerable, typecheck
from funcstructs.combinat import weak_compositions, divisors
from funcstructs.utils import split, subsequences

from .functions import rangefunc, Endofunction
from .multiset import Multiset
from .necklaces import Necklace, FixedContentNecklaces
from .rootedtrees import _levels_from_preim, DominantSequence, TreeEnumerator


__all__ = ("ConjugacyClass", "Funcstructs")


class ConjugacyClass(Multiset):
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
    it follows that ConjugacyClass(f) == ConjugacyClass(g) if and only if there
    exists a Bijection b such that f == b.conj(g).

    ConjugacyClass graphs are directed pseudoforests: Multisets of cycles
    (represented by Necklace objects) whose elements are unlabelled and
    unordered rooted trees (represented by DominantSequence objects).
    """

    __slots__ = ()

    def __new__(cls, f=()):
        if isinstance(f, Endofunction):
            cycles = []
            treenodes = f.acyclic_ancestors
            for cycle in f.cycles():
                trees = []
                for x in cycle:
                    # Use DominantSequence instead of RootedTree due to
                    # python's recursion limit, and for speed.
                    trees.append(
                        DominantSequence(_levels_from_preim(treenodes, x)))
                cycles.append(Necklace(trees))
            return super(ConjugacyClass, cls).__new__(cls, cycles)
        else:
            self = super(ConjugacyClass, cls).__new__(cls, f)
            for cycle in self._keys():
                if not isinstance(cycle, Necklace):
                    break
                for tree in cycle:
                    if not isinstance(tree, DominantSequence):
                        break
                else:
                    continue
                break
            else:
                return self
            raise TypeError("ConjugacyClass must have cycles of rooted trees")

    def __len__(self):
        """Number of nodes in the structure."""
        node_count = 0
        for cycle, mult in self._items():
            node_count += mult * sum(map(len, cycle))
        return node_count

    # Function.cycle_type is a property for
    # 1) Semantic similarity with Funcstructs.cycle_type
    # 2) In the VAST majority of cases, it is sublinear (< sqrt(n)) to compute.
    @property
    def cycle_type(self):
        """Return the type of a structure's cycle decomposition."""
        # Equivalent to Multiset(map(len, self)), but more efficient
        # in the case of highly degeneracy cycles.
        m = defaultdict(int)
        for cycle, mult in self._items():
            m[len(cycle)] += mult
        return Multiset(m)

    def degeneracy(self):
        """The number of ways to label a graph representing a particular
        endofunction with the given structure."""
        # First the degeneracy from the permutations of arrangements of cycles
        deg = super(ConjugacyClass, self).degeneracy()
        # Then account for the periodcity of each cycle
        for cycle, mult in self._items():
            cycledeg = cycle.degeneracy()
            # Finally the degeneracy of each rooted tree.
            for tree in cycle:
                cycledeg *= tree.degeneracy()
            deg *= cycledeg ** mult
        return deg

    def func_form(self):
        """Return a representative endofunction defined on range(n)."""
        # ::TODO:: Comments on process
        func = []
        root_node = end_node = 0
        for cycle in self:
            cycle_start = len(func)
            for tree in cycle:
                end_node += len(tree)
                # Form tree function labelled with the acyclic nodes
                func.extend(node+root_node for node in tree.parents())
                # Permute the cyclic nodes to form the cycle decomposition
                func[root_node] = end_node
                root_node = end_node
            func[root_node-len(tree)] = cycle_start
        return rangefunc(func)

    def imagepath(self):
        """Image path of an endofunction with the same structure."""
        cardinalities = [len(self), 0] + [0]*(len(self)-2)
        for cycle, mult in self._items():
            for tree in cycle:
                for subseq in subsequences.increasing(tree[1:]):
                    for it in subseq[:-1]:
                        cardinalities[subseq[-1]-it+1] -= mult
                    cardinalities[1] -= mult
        return tuple(compat.accumulate(cardinalities))[1:]


def _partitions(n):
    """Wrapper for D Eppstein's partitions returning multisets"""
    for partition in IntegerPartitions.partitions(n):
        yield Multiset(partition)


# The following algorithm for enumerating conjugacy classes of
# endofunctions was derived and implemented by Caleb C. Levy, from
# 2014 to 2015. To the best of his knowledge, this algorithm is novel.


# Enumerating Endofunction Structures with a Fixed Number of Nodes
# ================================================================
# We use enumerators of the following sets of objects without derivation:
# - Unordered rooted trees on a fixed number of nodes
# - Necklaces with a fixed (multi)set of beads
# - Weak compositions n into k parts
# - Partitions of n (into k parts)
# - Cartesian products of given sets
# - Combinations with replacement from a given set
#
# Please note that while none of the above are trivial to implement, we
# do not discuss them further here. (TODO: link to their modules).
#
#
# "Groups of Forests" vs "Cycles with Trees"
# ------------------------------------------
# Viewed strictly as graphs, endofunction structures are simply unlabelled
# (directed *) pseudoforests (https://en.wikipedia.org/wiki/Pseudoforest).
# They may be viewed equivalently as either (1) trees grouped together in
# cycles, or as (2) cycles with rooted trees attached to them. For the
# purposes of this algorithm we emphasize (2), although this module once
# featured an enumerator based on (1).
#
# The old algorithm simply enumerated all forests (a multiset of rooted
# trees) on a fixed number of nodes, grouped them together in multiset
# partitions, and generated unordered cartesian products of the Necklaces
# whose elements were from the multisets.
#
# This might have been more straightforward if enumerating multiset
# partitions were not so difficult. Sympy is the the only library I am
# aware of with this functionality (in python, anyway), and at over 1000
# lines, it exceeds the combined complexity of every other part of the
# algorithm!
#
# So using (1) actually added substantial complexity to the total
# process, and turned out to be slower (by ~4x) at the set sizes we were
# interested in. Adding a sympy dependency also greatly increased import
# time and restricted compatibility with other python implementations.
# Finally, method (2) had the added benefit of answering the more general
# question of enumerating endofunction structures of a given cycle type.
#
# * They need not be directed if we distinguish between psudoforest
#   components which are mirrors, but NOT rotations, of each other. This
#   distinction is important but subtle. (TODO: Add example with brute
#   force conjugating)
#
# Cycle Types
# -----------
# Viewpoint (2) is suggestive of looking at transformation monoids as
# generalizations of the symmetric group. We define a node of an
# endofunction as "cyclic" if it is in a cycle (or the root of a tree).
# The remaining nodes are called "tree" nodes.
#
# The "cycle type" of an endofunction is the cycle type of the permutation
# obtained by removing all of the tree nodes. This may be any partition
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
# Our next task is two-fold: (a) forming trees with the remaining tree
# nodes and (b) enumerating ways of attaching them to the partition of
# cycles. Problem (a) is solved via our black box, so we focus mainly on
# (b).
#
# The underlying permutation may be divided into "components": groups of
# cycles with the same length. No matter how the tree nodes are connected
# to each other or to the cyclic nodes, any endofunctions with distinct
# allocations of tree nodes will have different structure. (TODO: find
# which step in the twelve-fold path this is).
#
# Let n be the total number of tree nodes and k be the number of
# distinct cycle lengths. If we impose an (arbitrary) ordering on the
# components, these allocations will correspond to weak compositions of n
# into k parts.
#
# A "component group" is a component with rooted trees attached to it.
# Once we have a mechanism to enumerate component groups formable from a
# component and a set of tree nodes, we take the cartesian product of
# each set of component groups to get the endofunction structures
# corresponding to a weak composition of tree nodes.
#
# The next section describes such a mechanism.


def cycle_type_funcstructs(node_count, cycle_type):
    """Enumerate all conjugacy classes with the given node count and cycle
    type."""
    n = node_count - sum(cycle_type)
    k = cycle_type.num_unique_elements()
    lengths, mults = split(cycle_type)
    for composition in weak_compositions(n, k):
        cycle_groups = []
        for c, l, m in zip(composition, lengths, mults):
            cycle_groups.append(component_groups(c, l, m))
        for bundle in product(*cycle_groups):
            yield Multiset.__new__(ConjugacyClass, chain(*bundle))


# Twelve-Fold Path: Item #10
# --------------------------
# Consider a component with m cycles of length l. We wish enumerate every
# component group we can form by connecting t tree nodes to themselves or
# the cycles.
#
# Our first step for enumerating component groups is allocating the tree
# nodes amongst the cycles of the component. Prior to attaching the
# trees, neither the cycles (bins) nor the nodes (balls) are
# distinguishable (labelled) from each other, thus the problem reduces
# directly to distributing t unlabelled balls into m unlabelled boxes.
#
# This is problem ten in the "Twelve-Fold Path" (see the references), and
# it is solved by enumerating partitions of t into at most m parts, or
# equivalently, partitions of t+m into exactly m parts. The latter proves
# more convenient for our purposes.


def direct_unordered_attachments(t, m):
    """Enumerate the ways of directly attaching t unlabelled free nodes to l
    unlabelled nodes."""
    return IntegerPartitions.fixed_length_partitions(t+m, m)


# Unordered Product
# -----------------
# We refer to any way of attaching tree nodes to themselves or a cycle as
# an "attachment". Supposing we can enumerate attachments of p nodes to a
# cycle of length l, we can then take an "unordered" cartesian product of
# the sets of attachments to each cycle to generate the component groups
# for a given allocation of nodes.
#
# Here we define the unordered product of sets (A_1, A_2, ..., A_m) as
# the set of all distinct multisets of length m containing precisely one
# element from each A_i, where i goes between 1 and m. For general sets,
# unordered products are fairly complicated, however we can exploit
# certain aspects of our situation.
#
# First note that the unordered product of pair-wise disjoint sets is
# isomorphic to the ordered product of any fixed ordering of those sets.
# Second, we notice that the elements of an unordered product of a set
# with itself are simply combinations with replacement from elements of
# that set.
#
# Our sets of attachment are "pseudo-orthogonal": if they have the same
# number of free tree nodes, they are equal; otherwise they are disjoint.
# For a given partition of tree nodes amongst the cycles of the
# component, we first group by number of attached tree nodes and form
# combinations of them with replacement, and then take cartesian products
# of those sets of combinations.


def _unordered_product(mset, iterfunc):
    """Given a multiset of inputs to an iterable, and iterfunc, returns all
    unordered combinations of elements from iterfunc applied to each el. It is
    equivalent to:

        set(Multiset(p) for p in product(*[iterfunc(i) for i in mset]))

    except it runs through each element once. This program makes the
    assumptions that no two members of iterfunc(el) are the same, and that if
    el1 != el2 then iterfunc(el1) and iterfunc(el2) are mutually disjoint."""
    mset = Multiset(mset)
    strands = []
    for y, d in mset._items():
        strands.append(combinations_with_replacement(iterfunc(y), d))
    for bundle in product(*strands):
        yield chain(*bundle)


# The "unorderedness" of the product is an important and subtle detail.
# It is a degeneracy that only shows up for larger node counts. It also
# prevents our algorithm from being "resumable"; given an endofunction
# structure, one cannot deduce the next one from it alone. (TODO: fill
# this detail in, establish min node bound).
#
# All that remains is to enumerate attachments of p nodes onto a cycle of
# length l.


def component_groups(t, l, m):
    """Enumerate ways to make rooted trees from t free nodes and attach
    them to a group of m cycles of length l.
    """
    for partition in direct_unordered_attachments(t, m):
        for cycle_group in _unordered_product(
                partition,
                # Each element of the partition corresponds to a cycle.
                # Due to the way they are enumerated, each bin of the
                # partition has an extra node, which must be taken
                # out, hence the "y-1" term
                lambda y: attachment_forests(y-1, l)):
            # must expand out into list or else the chain object will
            # be consumed when taking the product of the component groups
            yield list(cycle_group)


# Attachments
# -----------
# At this point we have a cycle of length l, and p tree nodes to attach
# to it. Without ordering, each attachment is simply a forest with l
# trees and l+p nodes.
#
# We can reuse our allocater of unlabelled balls into unlabelled boxes to
# enumerate all partitions of p nodes into l bins. The set of forests on
# each partition is the unordered product of the sets of trees formable
# from each bin of nodes.
#
# For any one such forest, the cycles are simply all of the orderings of
# those trees which are distinct up to rotation. These are given by our
# enumerator of necklaces with fixed content, where the forests comprise
# the content.
#
# Thus, to find the attachments, we enumerate every forest with precisely
# as many trees as there are elements in the cycle, then enumerate the
# necklaces whose elements are the trees of the forest.


def attachment_forests(t, l):
    """Enumerate all ways to make rooted trees from t free nodes and attach
    them to a a cycle of length l."""
    for partition in direct_unordered_attachments(t, l):
        # TODO: get rid of duplicate Multiset madness here
        for forest in _unordered_product(partition, TreeEnumerator):
            for necklace in FixedContentNecklaces(forest):
                yield necklace


class Funcstructs(Enumerable):
    """Enumerator of endofunction structures consisting of n nodes,
    optionally restricted to a given cycle type. The following invariant
    holds for any n:

    set(Funcstructs(n)) == set(map(ConjugacyClass, TransformationMonoid(n)))
    for any non-negative integer n.
    """

    def __init__(self, n, cycle_type=None):
        if not(compat.is_index(n) and n >= 0):
            raise ValueError("Cannot define funcstructs on %s nodes" % n)
        if cycle_type is not None:
            cycle_type = Multiset(cycle_type)
            if not all(map(compat.is_natural, cycle_type._keys())):
                raise TypeError("A cycle type must be an integer partition")
        self.n = n
        self.cycle_type = cycle_type

    def __iter__(self):
        if self.cycle_type is None:
            return integer_funcstructs(self.n)
        else:
            return cycle_type_funcstructs(self.n, self.cycle_type)

    @typecheck(ConjugacyClass)
    def __contains__(self, other):
        if len(other) == self.n:
            if self.cycle_type is not None:
                return self.cycle_type == other.cycle_type
            return True
        return False

    def cardinality(self):
        """Count the number of endofunction structures on n nodes.

        Based on De Bruijn, N.G., "Enumeration of Mapping Patterns",
        Journal of Combinatorial Theory, Volume 12, 1972. See the papers
        directory for the original reference."""
        tot = 0
        for part in _partitions(self.n):
            p = 1
            for i in range(1, self.n+1):
                s = sum(j*part.get(j, 0) for j in divisors(i))
                b = part.get(i, 0)
                p *= s**b * Fraction(i, 1)**(-b)/factorial(b)
            tot += p
        return int(tot)
