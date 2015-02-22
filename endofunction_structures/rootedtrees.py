#!/usr/bin/env python
# Copyright (C) 2014-2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.

""" A rooted tree is a connected digraph with a single cycle such that every
node's outdegree and every cycle's length is exactly one. Alternatively, it is
a tree with a designated "root" node, where every path ends with the root. They
are equivalent to filesystems consisting entirely of folders with no symbolic
links. An unlabelled rooted tree is the equivalence class of a given directory
where folders in each subdirectory may be rearranged in any desired order
(alphabetical, reverse-alphabetical, date added, or any other labelling). A
forest is any collection of rooted trees.

Any endofunction structure may be represented as a forest of trees, grouped
together in multisets corresponding to cycle decompositions of the final set
(the subset of its domain on which it is invertible). The orderings of the
trees in the multisets correspond to necklaces whose beads are the trees
themselves. """



import math
import functools

from . import subsequences
from . import multiset
from . import factorization
from . import productrange


@functools.total_ordering
class RootedTree(object):

    def __init__(self, subtrees=None):
        # there is no root; this is totally structureless.
        if subtrees is None:
            subtrees = multiset.Multiset()
        subtrees = multiset.Multiset(subtrees)
        for subtree in subtrees.elements():
            if not isinstance(subtree, RootedTree):
                raise ValueError("Subtrees must be rooted trees.")
        self.subtrees = subtrees

    def __hash__(self):
        return hash(self.subtrees)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.subtrees == other.subtrees
        return False

    def __ne__(self, other):
        return not self == other

    def __bool__(self):
        if self.subtrees:
            return True
        return False

    def _str(self):
        if not self:
            return '{}'
        else:
            strings = []
            for subtree in sorted(self.subtrees.keys(), reverse=1):
                # Hack to make tree print with multiplicity exponents.
                mult = self.subtrees.count(subtree)
                tree_string = subtree._str()
                if mult > 1:
                    tree_string += '^%s' % str(mult)
                strings.append(tree_string)
            return '{%s}' % ', '.join(strings)

    def __lt__(self, other):
        if isinstance(other, type(self)):
            return self.ordered_form() < other.ordered_form()
        return False

    def __str__(self):
        return "RootedTree(%s)" % self._str()

    def __repr__(self):
        if not self:
            return 'RootedTree()'
        return "RootedTree([%s])" % repr(self.subtrees)[10:-2]

    def degeneracy(self):
        """Return #(nodes)!/#(labellings)"""
        if not self:
            return 1
        deg = self.subtrees.degeneracy()
        for subtree in self.subtrees:
            deg *= subtree.degeneracy()
        return deg

    def _ordered_level_sequence(self, level=1):
        level_sequence = [level]
        for tree in self.subtrees:
            level_sequence.extend(tree._ordered_level_sequence(level+1))
        return level_sequence

    def ordered_form(self):
        return DominantTree(self._ordered_level_sequence())


@functools.total_ordering
class LevelTree(object):
    """Represents an unlabelled ordered rooted tree."""

    def __repr__(self):
        return self.__class__.__name__ + "("+str(list(self.level_sequence))+')'

    def __eq__(self, other):
        if isinstance(other, LevelTree):
            return self.level_sequence == other.level_sequence
        else:
            return False

    def __ne__(self, other):
        return not self == other

    def __lt__(self, other):
        if isinstance(other, LevelTree):
            return self.level_sequence < other.level_sequence
        else:
            raise ValueError("Cannot compare tree with type %s" % type(other))

    def __hash__(self):
        return hash(self.level_sequence)

    def __len__(self):
        return len(self.level_sequence)

    def __iter__(self):
        return iter(self.level_sequence)

    def __bool__(self):
        return True

    __nonzero__ = __bool__

    def branch_sequences(self):
        """ Return each major subbranch of a tree (even chopped). """
        if len(self.level_sequence) == 1:
            return
        isroot = lambda node: node == self.level_sequence[0] + 1
        for branch in subsequences.startswith(self.level_sequence[1:], isroot):
            yield branch

    def subtree_sequences(self):
        """Generate the main subtrees of self in order."""
        for branch_sequence in self.branch_sequences():
            yield [node-1 for node in branch_sequence]

    def bracket_form(self):
        """
        Return a representation the rooted tree via nested lists. This method
        is a novelty item, and shouldn't be used for anything practical.
        """
        if not self.branch_sequences():
            return []
        return [subtree.bracket_form() for subtree in self.subtrees()]

    def unordered(self):
        if not self.branch_sequences():
            return RootedTree()
        return RootedTree(subtree.unordered() for subtree in self.subtrees())

    def labelled_sequence(self, labels=None):
        """ Return an endofunction whose structure corresponds to the rooted
        tree. The root is 0 by default, but can be permuted according a
        specified labelling. """

        if labels is None:
            labels = range(len(self.level_sequence))
        height = max(self.level_sequence)
        labelling = [0]*len(self.level_sequence)
        labelling[0] = labels[0]
        height_prev = 1
        # Most recent node found at height h. Where to graft the next node to.
        grafting_point = [0]*height
        for node, height in enumerate(self.level_sequence[1:]):
            if height > height_prev:
                labelling[node+1] = labels[grafting_point[height_prev-1]]
                height_prev += 1
            else:
                labelling[node+1] = labels[grafting_point[height-2]]
                height_prev = height
            grafting_point[height-1] = node+1
        return labelling


class OrderedTree(LevelTree):

    def __init__(self, level_sequence):
        self.level_sequence = tuple(level_sequence)

    def branches(self):
        for branch in self.branch_sequences():
            yield self.__class__(branch)

    def subtrees(self):
        for subtree in self.subtree_sequences():
            yield self.__class__(subtree)

    def _dominant_sequence(self):
        """ Return the lexicographically dominant rooted tree corresponding to
        self. """
        if not self.branches():
            return self.level_sequence
        branch_list = []
        for branch in self.branches():
            branch_list.append(branch._dominant_sequence())
        branch_list.sort(reverse=True)
        return tuple([self.level_sequence[0]] + productrange.flatten(branch_list))

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

    def __init__(self, level_sequence, preordered=False):
        if preordered:
            self.level_sequence = tuple(level_sequence)
        elif isinstance(level_sequence, type(self)):
            self.level_sequence = level_sequence.level_sequence
        else:
            self.level_sequence = dominant_sequence(level_sequence)

    def branches(self):
        for branch in self.branch_sequences():
            yield self.__class__(branch, preordered=True)

    def subtrees(self):
        for subtree in self.subtree_sequences():
            # Subtrees of a dominant tree are by definition dominant, so no
            # need to check.
            yield self.__class__(subtree, preordered=True)

    def chop(self):
        """ Return a multiset of the input tree's main sub branches. """
        return multiset.Multiset(subtree for subtree in self.subtrees())

    def degeneracy(self):
        """ To calculate the degeneracy of a collection of subtrees you
        start with the lowest branches and then work upwards. If a group of
        identical subbranches are connected to the same node, we multiply
        the degeneracy of the tree by the factorial of the multiplicity of
        these subbranches to account for their distinct orderings. The same
        principal applies to subtrees.

        TODO: A writeup of this with diagrams will be in the notes. """
        logs = self.chop()
        if not logs:
            return 1
        deg = 1
        for subtree in logs:
            deg *= subtree.degeneracy()
        return deg*logs.degeneracy()


class TreeEnumerator(object):

    """Represents the class of unlabelled rooted trees on n nodes."""

    def __init__(self, node_count):
        if node_count < 1:
            raise ValueError("Every tree requires at least one node.")
        self.n = node_count
        self._len = None

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
        return self.__class__.__name__+'('+str(self.n)+')'

    def __iter__(self):
        """ Takes an integer N as input and outputs a generator object
        enumerating all isomorphic unlabeled rooted trees on N nodes.

        The basic idea of the algorithm is to represent a tree by its level
        sequence: list each vertice's height above the root, where vertex v+1
        is connected either to vertex v or the previous node at some lower
        level.

        Choosing the lexicographically greatest level sequence gives a
        canonical representation for each rooted tree. We start with the
        tallest rooted tree given by T=range(1,N+1) and then go downward,
        lexicographically, until we are flat so that T=[1]+[2]*(N-1).

        Algorithm and description provided in: T. Beyer and S. M. Hedetniemi.
        "Constant time generation of rooted trees." Siam Journal of
        Computation, Vol. 9, No. 4. November 1980. """
        tree = [I+1 for I in range(self.n)]
        yield DominantTree(tree, preordered=True)
        if self.n > 2:
            while tree[1] != tree[2]:
                p = self.n-1
                while tree[p] == tree[1]:
                    p -= 1
                q = p-1
                while tree[q] >= tree[p]:
                    q -= 1
                for I in range(p, self.n):
                    tree[I] = tree[I-(p-q)]
                yield DominantTree(tree, preordered=True)

    def cardinality(self):
        """Returns the number of rooted tree structures on n nodes. Algorithm
        featured without derivation in Finch, S. R. "Otter's Tree Enumeration
        Constants." Section 5.6 in "Mathematical Constants", Cambridge,
        England: Cambridge University Press, pp. 295-316, 2003. """
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

    def __len__(self):
        """ NOTE: For n >= 47, len(TreeEnumerator(n)) is greater than C long,
        and thus gives rise to an index overflow error. Use self.cardinality
        instead. """
        if self._len is None:
            self._len = self.cardinality()
        return self._len


class ForestEnumerator(TreeEnumerator):
    """ Any rooted tree on N+1 nodes can be identically described by a
    collection of rooted trees on N nodes, grafted together at a single root.

    To enumerate all collections of rooted trees on N nodes, we reverse the
    principle and enumerate all rooted trees on N+1 nodes, chopping them at the
    base. Much simpler than finding all trees corresponding to a partition. """

    def __init__(self, node_count):
        self.n = node_count + 1
        self._len = None

    def __repr__(self):
        return self.__class__.__name__+'('+str(self.n - 1)+')'

    def __iter__(self):
        for tree in super(ForestEnumerator, self).__iter__():
            yield tree.chop()


class PartitionForests(object):
    """Colections of rooted trees with sizes specified by partitions."""
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

    def __len__(self):
        l = 1
        for y, r in self.partition.items():
            n = len(TreeEnumerator(y))
            l *= math.factorial(n+r-1)//math.factorial(r)//math.factorial(n-1)
        return l

    def __iter__(self):
        return productrange.unordered_product(self.partition, TreeEnumerator)

    def __repr__(self):
        return self.__class__.__name__+'('+str(list(self.partition))+')'
