# Copyright (C) 2014-2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.

""" Algorithms for representing and enumerating unlabelled rooted trees:
connected directed graphs with a single length-one cycle and nodes of
out-degree one. A forest is any collection of rooted trees. """

from memoized_property import memoized_property

from . import counts
from . import subsequences
from . import multiset
from . import factorization
from . import productrange


class RootedTree(multiset.Multiset):
    """An unlabelled, unordered rooted tree; i.e. the ordering of the subtrees
    is unimportant. Since there is nothing to distinguish the nodes, we
    characterize a rooted tree strictly by the multiset of its subtrees.
    """

    def __new__(cls, subtrees=None):
        if isinstance(subtrees, cls):
            return subtrees
        self = super(RootedTree, cls).__new__(cls, subtrees)
        if not all(isinstance(tree, cls) for tree in self.unique_elements()):
            raise TypeError("subtrees must be rooted trees")
        return self

    __bool__ = __nonzero__ = lambda self: True  # roots make trees nonempty

    def _str(self):
        strings = []
        for subtree in sorted(self.keys(), reverse=1):
            # Hack to make tree print with multiplicity exponents.
            mult = self[subtree]
            tree_string = subtree._str()
            if mult > 1:
                tree_string += '^%s' % mult
            strings.append(tree_string)
        return '{%s}' % ', '.join(strings)

    def __lt__(self, other):
        if isinstance(other, type(self)):
            return self.ordered_form() < other.ordered_form()
        return NotImplemented

    def __str__(self):
        return self.__class__.__name__+"(%s)" % self._str()

    def __repr__(self):
        return self.__class__.__name__+"(%s)" % list(self)

    def degeneracy(self):
        """Return #(nodes)!/#(labellings)"""
        deg = super(RootedTree, self).degeneracy()
        for subtree, mult in self.items():
            deg *= subtree.degeneracy()**mult
        return deg

    def _ordered_level_sequence(self, level=1):
        level_sequence = [level]
        for tree in self:
            level_sequence.extend(tree._ordered_level_sequence(level+1))
        return level_sequence

    def ordered_form(self):
        return DominantTree(self._ordered_level_sequence())


class LevelTree(tuple):
    """Data structure for representing ordered trees by a level sequence: a
    listing of each node's height above the root produced in depth-first
    traversal order. The tree is reconstructed by connecting each node to
    previous one directly below its height.
    """

    def __new__(cls, *args, **kwargs):
        raise NotImplementedError(
            "LevelTree should not be invoked directly. Use either OrderedTree "
            "or DominantTree."
        )

    def __repr__(self):
        return self.__class__.__name__+"(%s)" % list(self)

    def branch_sequences(self):
        """ Return each major subbranch of a tree (even chopped). """
        isroot = lambda node: node == self[0] + 1
        for branch in subsequences.startswith(self[1:], isroot):
            yield branch

    def subtree_sequences(self):
        """Generate the main subtrees of self in order."""
        for branch_sequence in self.branch_sequences():
            yield [node-1 for node in branch_sequence]

    def bracket_form(self):
        """ Return a representation of the rooted tree via nested lists. This
        method is a novelty item, and shouldn't be used for anything practical.
        """
        if not self.branch_sequences():
            return []
        return [subtree.bracket_form() for subtree in self.subtrees()]

    def unordered(self):
        """Return the unordered tree corresponding to the rooted tree."""
        if not self.branch_sequences():
            return RootedTree()
        return RootedTree(subtree.unordered() for subtree in self.subtrees())

    def labelled_sequence(self, labels=None):
        """Return an endofunction whose structure corresponds to the rooted
        tree. The root is 0 by default, but can be permuted according a
        specified labelling.
        """
        if labels is None:
            labels = range(len(self))
        height = max(self)
        labelling = [0]*len(self)
        labelling[0] = labels[0]
        height_prev = 1
        # Most recent node found at height h. Where to graft the next node to.
        grafting_point = [0]*height
        for node, height in enumerate(self[1:], start=1):
            if height > height_prev:
                labelling[node] = labels[grafting_point[height_prev-1]]
                height_prev += 1
            else:
                labelling[node] = labels[grafting_point[height-2]]
                height_prev = height
            grafting_point[height-1] = node
        return labelling


class OrderedTree(LevelTree):
    """An unlabelled ordered tree represented by its level sequence."""

    def __new__(cls, level_sequence):
        if isinstance(level_sequence, cls):
            return level_sequence
        return tuple.__new__(cls, level_sequence)

    def branches(self):
        for branch in self.branch_sequences():
            yield self.__class__(branch)

    def subtrees(self):
        for subtree in self.subtree_sequences():
            yield self.__class__(subtree)

    def _dominant_sequence(self):
        """Return the dominant rooted tree corresponding to self."""
        branch_list = []
        for branch in self.branches():
            branch_list.append(branch._dominant_sequence())
        branch_list.sort(reverse=True)
        return [self[0]] + productrange.flatten(branch_list)

    def canonical_form(self):
        """Return a dominant tree type."""
        return DominantTree(self)


def dominant_sequence(level_sequence):
    """Return the dominant form of a level sequence."""
    return OrderedTree(level_sequence)._dominant_sequence()


def unordered_tree(level_sequence):
    """Return the unordered tree corresponding to the given level sequence."""
    return OrderedTree(level_sequence).unordered()


class DominantTree(LevelTree):
    """A dominant tree is the ordering of an unordered tree with
    lexicographically largest level sequence. It is formed by placing all
    subtrees in dominant form and then putting them in descending order.
    """

    def __new__(cls, level_sequence, preordered=False):
        if isinstance(level_sequence, cls):
            return level_sequence
        if not preordered:
            level_sequence = dominant_sequence(level_sequence)
        return tuple.__new__(cls, level_sequence)

    def branches(self):
        for branch in self.branch_sequences():
            # Subtrees of dominant trees are dominantly ordered by construction
            yield self.__class__(branch, preordered=True)

    def subtrees(self):
        for subtree in self.subtree_sequences():
            yield self.__class__(subtree, preordered=True)

    def chop(self):
        """Return a multiset of the input tree's main sub branches."""
        return multiset.Multiset(subtree for subtree in self.subtrees())

    def degeneracy(self):
        """The number of representations of each labelling of the unordered
        tree corresponding to self is found by multiplying the product of the
        degeneracies of all the subtrees by the degeneracy of the multiset
        containing the rooted trees.

        TODO: A writeup of this with diagrams will be in the notes.
        """
        logs = self.chop()
        if not logs:
            return 1
        deg = 1
        for subtree in logs:
            deg *= subtree.degeneracy()
        return deg*logs.degeneracy()


class TreeEnumerator(object):
    """Represents the class of unlabelled rooted trees on n nodes."""

    __slots__ = ['n', '_cardinality']

    def __init__(self, node_count):
        if node_count < 1:
            raise ValueError("Every tree requires at least one node.")
        self.n = node_count

    def __hash__(self):
        return hash(self.n)

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.n == other.n
        return False

    def __ne__(self, other):
        return not self == other

    __le__ = None

    def __repr__(self):
        return self.__class__.__name__+'(%s)' % self.n

    def __iter__(self):
        """Generates the dominant representatives of each unordered tree in
        lexicographic order, starting with the tallest tree with level sequence
        range(1, n+1) and ending with [1]+[2]*(n-1).

        Algorithm and description provided in T. Beyer and S. M. Hedetniemi,
        "Constant time generation of rooted trees." Siam Journal of
        Computation, Vol. 9, No. 4. November 1980.
        """
        tree = [i+1 for i in range(self.n)]
        yield DominantTree(tree, preordered=True)
        if self.n > 2:
            while tree[1] != tree[2]:
                p = self.n-1
                while tree[p] == tree[1]:
                    p -= 1
                q = p-1
                while tree[q] >= tree[p]:
                    q -= 1
                for i in range(p, self.n):
                    tree[i] = tree[i-(p-q)]
                yield DominantTree(tree, preordered=True)

    @memoized_property
    def cardinality(self):
        """Returns the number of rooted tree structures on n nodes. Algorithm
        featured without derivation in Finch, S. R. "Otter's Tree Enumeration
        Constants." Section 5.6 in "Mathematical Constants", Cambridge,
        England: Cambridge University Press, pp. 295-316, 2003.
        """
        T = [0, 1] + [0]*(self.n - 1)
        for n in range(2, self.n + 1):
            for i in range(1, self.n):
                s = 0
                for d in factorization.divisors(i):
                    s += T[d]*d
                s *= T[n-i]
                T[n] += s
            T[n] //= n-1
        return T[-1]


class ForestEnumerator(TreeEnumerator):
    """Represents the class of collections of rooted trees on n nodes."""

    __slots__ = ['n', '_cardinality']

    def __init__(self, node_count):
        self.n = node_count + 1

    def __repr__(self):
        return self.__class__.__name__+'(%s)' % (self.n - 1)

    def __iter__(self):
        """Any rooted tree on n+1 nodes can be identically described as a
        collection of rooted trees on n nodes, grafted together at a single
        root. To enumerate all collections of rooted trees on n nodes, we may
        enumerate all rooted trees on n+1 nodes, chopping them at the base.
        """
        for tree in super(ForestEnumerator, self).__iter__():
            yield tree.chop()


class PartitionForests(object):
    """Collections of rooted trees with sizes specified by partitions."""

    __slots__ = ['partition', '_cardinality']

    def __init__(self, partition):
        self.partition = multiset.Multiset(partition)

    def __hash__(self):
        return hash(self.partition)

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.partition == other.partition
        return False

    def __ne__(self, other):
        return not self == other

    __le__ = None

    @memoized_property
    def cardinality(self):
        l = 1
        for y, r in self.partition.items():
            n = TreeEnumerator(y).cardinality
            l *= counts.nCWRk(n, r)
        return l

    def __iter__(self):
        return productrange.unordered_product(self.partition, TreeEnumerator)

    def __repr__(self):
        return self.__class__.__name__+'(%s)' % list(self.partition)
