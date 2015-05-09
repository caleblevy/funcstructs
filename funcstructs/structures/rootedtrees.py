"""Algorithms for representing and enumerating unlabelled rooted trees:
connected directed graphs with a single length-one cycle and nodes of
out-degree one. A forest is any collection of rooted trees.

Caleb Levy, 2014 and 2015.
"""

from collections import defaultdict

from . import (
    bases,
    combinat,
    factorization,
    multiset,
    subsequences,
)
from . import _treefuncs
from .utils import flatten

__all__ = [
    "OrderedTree", "DominantTree", "RootedTree",
    "TreeEnumerator", "ForestEnumerator", "PartitionForests"
]


class OrderedTree(bases.Tuple):
    """Data structure for representing ordered trees by a level sequence: a
    listing of each node's height above the root produced in depth-first
    traversal order. The tree is reconstructed by connecting each node to
    previous one directly below its height.
    """

    __slots__ = ()

    @classmethod
    def from_func(cls, func, root=None):
        """Return the level sequence of the rooted tree formed from the graph
        of all noncyclic nodes whose iteration paths pass through node. If no
        node is specified, and the function does not have a unique cyclic
        element, a ValueError is raised."""
        if root is None:
            root = next(iter(func.limitset))
            if len(func.limitset) != 1:
                raise ValueError("Function structure is not a rooted tree")
        # Must have separate method for endofunction since default is level seq
        return cls(_treefuncs.levels_from_preim(func.acyclic_ancestors, root))

    def _branch_sequences(self):
        return subsequences.startswith(self[1:], self[0]+1)

    def branches(self):
        """Return each major subbranch of a tree."""
        for branch in self._branch_sequences():
            yield self.__class__(branch)

    def chop(self):
        """Return a multiset of the input tree's main sub branches."""
        return multiset.Multiset(self.branches())

    def traverse_map(self, mapping=list):
        """Apply mapping to the sequence of mapping applied to the subtrees."""
        return mapping(tree.traverse_map(mapping) for tree in self.branches())

    def map_labelling(self, labels=None):
        """Viewing the ordered level sequence as an implicit mapping of each
        node to the most recent node of the next lowest level, return the
        sequence of elements that each node is mapped to. If labels is given,
        func_labelling[n] -> labels[func_labelling[n]]. """
        if labels is None:
            labels = range(len(self))
        for n, l, f in _treefuncs.funclevels_iterator(self):
            yield labels[f]

    def breadth_first_traversal(self):
        """Return nodes in breadth-first traversal order"""
        return flatten(_treefuncs.treefunc_properties(self)[2])


def _dominant_keys(height_groups, func):
    """Assign to each node a key for sorting"""
    node_keys = defaultdict(list)  # node_keys[node] <-> sort key for node
    levels = reversed(height_groups)
    previous_level = next(levels)
    # sort_value will increase to produce dominant tree
    sort_value = 1
    for x in previous_level:
        node_keys[x] = sort_value  # Top nodes are all identical
    for level in levels:
        # enumerate for connections from previous level to current
        for x in previous_level:
            node_keys[func[x]].append(node_keys[x])
        # Sort attachments to nodes of level by value of their subtrees
        # Make a sorted list copy, since iteration order matters
        sorted_nodes = sorted(level, key=node_keys.__getitem__)
        # Make copy of sorting keys; they will be overwritten in the loop
        sorting_keys = map(node_keys.get, sorted_nodes)
        # Overwrite sorting keys to prevent accumulation of nested lists
        for run in subsequences.runs(zip(sorted_nodes, sorting_keys),
                                     lambda x, y: x[1] == y[1]):
            sort_value += 1
            for x in run:
                node_keys[x[0]] = sort_value
        previous_level = reversed(sorted_nodes)
    return node_keys


class DominantTree(OrderedTree):
    """A dominant tree is the ordering of an unordered tree with
    lexicographically largest level sequence. It is formed by placing all
    subtrees in dominant form and then putting them in descending order.
    """

    __slots__ = ()

    def __new__(cls, level_sequence, preordered=False):
        if not(preordered or isinstance(level_sequence, cls)):
            f, p, g = _treefuncs.treefunc_properties(level_sequence)
            keys = _dominant_keys(g, f)
            level_sequence = _treefuncs.levels_from_preim(p, 0, keys)
        return super(DominantTree, cls).__new__(cls, level_sequence)

    def branches(self):
        for branch in self._branch_sequences():
            # Subtrees of dominant trees are dominantly ordered by construction
            yield self.__class__(branch, preordered=True)

    def degeneracy(self):
        """The number of representations of each labelling of the unordered
        tree corresponding to self is found by multiplying the product of the
        degeneracies of all the subtrees by the degeneracy of the multiset
        containing the rooted trees.

        TODO: A writeup of this with diagrams will be in the notes.
        """
        logs = self.chop()
        deg = logs.degeneracy()
        for subtree, mult in logs.items():
            deg *= subtree.degeneracy()**mult
        return deg


class RootedTree(multiset.Multiset):
    """An unlabelled, unordered rooted tree; i.e. the ordering of the subtrees
    is unimportant. Since there is nothing to distinguish the nodes, we
    characterize a rooted tree strictly by the multiset of its subtrees.
    """

    __slots__ = ()

    def __new__(cls, subtrees=None):
        if isinstance(subtrees, cls):
            return subtrees
        self = super(RootedTree, cls).__new__(cls, subtrees)
        if not all(isinstance(tree, cls) for tree in self.keys()):
            raise TypeError("subtrees must be rooted trees")
        return self

    @classmethod
    def from_levels(cls, levels):
        """Return the unordered tree corresponding to the level sequence."""
        return OrderedTree(levels).traverse_map(cls)

    def __bool__(self):
        return True  # All trees have roots, thus aren't empty

    __nonzero__ = __bool__

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

    def degeneracy(self):
        """Return #(nodes)!/#(labellings)"""
        deg = super(RootedTree, self).degeneracy()
        for subtree, mult in self.items():
            deg *= subtree.degeneracy()**mult
        return deg

    def _ordered_level_sequence(self, level=0):
        level_sequence = [level]
        for tree in self:
            level_sequence.extend(tree._ordered_level_sequence(level+1))
        return level_sequence

    def ordered_form(self):
        return DominantTree(self._ordered_level_sequence())


class TreeEnumerator(bases.Enumerable):
    """Represents the class of unlabelled rooted trees on n nodes."""

    def __init__(self, node_count, root_height=0):
        super(TreeEnumerator, self).__init__(node_count, None, 1)
        self.__root_height = root_height

    def __iter__(self):
        """Generates the dominant representatives of each unordered tree in
        lexicographic order, starting with the tallest tree with level sequence
        range(1, n+1) and ending with [1]+[2]*(n-1).

        Algorithm and description provided in T. Beyer and S. M. Hedetniemi,
        "Constant time generation of rooted trees." Siam Journal of
        Computation, Vol. 9, No. 4. November 1980.
        """
        tree = list(range(self.__root_height, self.n+self.__root_height))
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

    @property
    def cardinality(self):
        """Returns the number of rooted tree structures on n nodes. Algorithm
        featured without derivation in Finch, S. R. "Otter's Tree Enumeration
        Constants." Section 5.6 in "Mathematical Constants", Cambridge,
        England: Cambridge University Press, pp. 295-316, 2003."""
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


class ForestEnumerator(bases.Enumerable):
    """Represents the class of collections of rooted trees on n nodes."""

    def __init__(self, node_count):
        super(ForestEnumerator, self).__init__(node_count, None, 1)

    def __iter__(self):
        """Any rooted tree on n+1 nodes can be identically described as a
        collection of rooted trees on n nodes, grafted together at a single
        root. To enumerate all collections of rooted trees on n nodes, we may
        enumerate all rooted trees on n+1 nodes, chopping them at the base.
        """
        for tree in TreeEnumerator(self.n+1):
            yield tree.chop()

    @property
    def cardinality(self):
        return TreeEnumerator(self.n+1, -1).cardinality


class PartitionForests(bases.Enumerable):
    """Collections of rooted trees with sizes specified by partitions."""

    def __init__(self, partition):
        super(PartitionForests, self).__init__(None, partition)

    def __iter__(self):
        return multiset.unordered_product(self.partition, TreeEnumerator)

    @property
    def cardinality(self):
        l = 1
        for y, r in self.partition.items():
            n = TreeEnumerator(y).cardinality
            l *= combinat.nCWRk(n, r)
        return l
