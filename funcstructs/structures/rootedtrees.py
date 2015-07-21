"""Algorithms for representing and enumerating rooted trees.

Caleb Levy, 2014-2015.
"""

from itertools import chain, groupby
from math import factorial

from funcstructs import bases
from funcstructs.utils import combinat, factorization, subsequences

from funcstructs.structures.multiset import Multiset

__all__ = [
    "LevelSequence", "DominantSequence", "RootedTree",
    "TreeEnumerator", "forests"
]


def _levels_from_preim(graph, root=0, keys=None):
    """Return the level sequence of the ordered tree formed such that
    graph[x] are the nodes attached to x.

    Note: If the graph has any cycles, this method will not terminate.
    """
    if keys is not None:
        for connections in graph:
            connections.sort(key=keys.__getitem__)
    node_stack = [root]
    level = 0
    node_levels = {root: level}
    while node_stack:
        x = node_stack.pop()
        level = node_levels[x]
        yield level
        level += 1
        for y in graph[x]:
            node_stack.append(y)
            # Need to compute even for dominant tree, since levels will change
            node_levels[y] = level


class LevelSequence(bases.Tuple):
    """Representation of an unlabelled ordered tree using a level sequence.

    LevelSequence objects are obtained from OrderedTrees by listing
    each node's height above the root in post-ordered depth-first
    traversal. Numbering each node by its position in the sequence, the
    tree may be reconstructed by connecting each node to previous one
    directly below its height.

    Any valid level sequence may be used to make a LevelSequence object.

    Usage:

    >>> t = LevelSequence([0, 1, 1, 2, 3, 2])
    >>> t.traverse_map()                     # representation as nested lists
    [[], [[[]], []]]
    >>> t.traverse_map(tuple)                # can use any container type
    ((), (((),), ()))

    >>> list(t.breadth_first_traversal())
    [0, 1, 2, 3, 5, 4]

    >>> rangefunc(t.func_labelling())        # labelling as an Endofunction
    Endofunction({0: 0, 1: 0, 2: 0, 3: 2, 4: 3, 5: 2})
    """

    __slots__ = ()

    def __new__(cls, level_sequence):
        self = super(LevelSequence, cls).__new__(cls, level_sequence)
        previous_node = self[0]
        seen = set()
        for node in self[1:]:
            if node in seen:
                pass
            elif node == previous_node + 1:
                seen.add(node)
            else:
                raise ValueError("invalid level sequence: %s" % list(self))
            previous_node = node
        return self

    @classmethod
    def from_func(cls, func, root=None):
        """Return the level sequence of the rooted tree formed from the graph
        of all noncyclic nodes whose iteration paths pass through node. If no
        node is specified, and the function does not have a unique cyclic
        element, a ValueError is raised."""
        if root is None:
            lim = func.limitset()
            if len(lim) != 1:
                raise ValueError("Function structure is not a rooted tree")
            root = next(iter(lim))
        return cls(_levels_from_preim(func.acyclic_ancestors(), root))

    def parents(self):
        """Generator of the parent nodes of each node in order."""
        levels = iter(self)
        root = previous_level = next(levels)
        yield 0
        grafting_point = {0: 0}  # grafting_point[h] <-> last node at height h
        for node, level in enumerate(levels, start=1):
            if level > previous_level:
                parent = grafting_point[previous_level-root]
                previous_level += 1
            else:
                parent = grafting_point[level-root-1]
                previous_level = level
            yield parent
            grafting_point[level-root] = node

    def subtrees(self):
        """Return the subtrees attached to the root."""
        for branch in subsequences.startswith(self[1:], self[0]+1):
            # Bypass any constructor checks; since the tree is verified,
            # all of its subtrees must be as well.
            yield tuple.__new__(self.__class__, (node-1 for node in branch))

    def traverse_map(self, mapping=list):
        """Apply mapping to the sequence of mapping applied to the subtrees."""
        return mapping(tree.traverse_map(mapping) for tree in self.subtrees())

    def map_labelling(self, labels=None):
        """Viewing the ordered level sequence as an implicit mapping of each
        node to the most recent node of the next lowest level, return the
        sequence of elements that each node is mapped to. If labels is given,
        func_labelling[n] -> labels[func_labelling[n]]."""
        if labels is None:
            labels = range(len(self))
        return map(labels.__getitem__, self.parents())

    def height_groups(self):
        """Nodes in breadth-first traversal order grouped by height."""
        groups = [[] for _ in range(max(self) - self[0] + 1)]
        for node, height in enumerate(self):
            groups[height-self[0]].append(node)
        return groups

    def breadth_first_traversal(self):
        """Generate nodes in breadth-first traversal order."""
        return chain(*self.height_groups())

    def attachments(self):
        """Map of each node to the set of nodes attached to it in order."""
        preim = []
        for node, parent in enumerate(self.parents()):
            preim.append([])
            preim[parent].append(node)
        preim[0].pop(0)
        return preim


def _dominant_keys(height_groups, func, sort=True):
    """Assign to each node a key for sorting"""
    node_keys = [0]*len(func)  # node_keys[node] <-> sort key for node
    attachments = [[] for _ in func]  # attachments[x] <-> nodes attached to x
    previous_level = []
    sort_value = len(func)
    for level in reversed(height_groups):
        # enumerate for connections from previous level to current
        for x in previous_level:
            attachments[func[x]].append(node_keys[x])
        # Sort nodes of current level lexicographically by the keys of their
        # children. Since nodes of the previous level are already sorted, we
        # need not sort the attachments themselves.
        if sort is True:
            level.sort(key=attachments.__getitem__, reverse=True)
        # Assign int keys to current level to prevent accumulating nested lists
        for _, run in groupby(level, attachments.__getitem__):
            sort_value -= 1
            for x in run:
                node_keys[x] = sort_value
        previous_level = level
    return node_keys


class DominantSequence(LevelSequence):
    """A dominant tree is the ordering of an unordered tree with
    lexicographically largest level sequence. It is formed by placing all
    subtrees in dominant form and then putting them in descending order.
    """

    __slots__ = ()

    def __new__(cls, level_sequence):
        ot = LevelSequence(level_sequence)
        keys = _dominant_keys(ot.height_groups(), list(ot.parents()))
        level_sequence = _levels_from_preim(ot.attachments(), 0, keys)
        # No need to run LevelSequence checks; it's either been preordered or
        # treefunc_properties will serve as an effective check due to indexing.
        return super(LevelSequence, cls).__new__(cls, level_sequence)

    def degeneracy(self):
        """The number of representations of each labelling of the unordered
        tree corresponding to self is found by multiplying the product of the
        degeneracies of all the subtrees by the degeneracy of the multiset
        containing the rooted trees."""
        # TODO: A writeup of this with diagrams will be in the notes.
        deg = 1
        parents = list(self.parents())
        groups = self.height_groups()
        keys = _dominant_keys(groups, parents, sort=False)
        # Two nodes are interchangeable iff they have the same key and parent
        for _, g in groupby(chain(*groups), lambda x: (parents[x], keys[x])):
            deg *= factorial(len(list(g)))
        return deg


class RootedTree(Multiset):
    """An unlabelled, unordered rooted tree

    A RootedTree is a recursive data structure defined by the multiset
    of its subtrees. As all rooted trees have roots, thus are nonempty
    and evaluate True.
    """

    __slots__ = ()

    def __new__(cls, subtrees=()):
        if isinstance(subtrees, LevelSequence):
            return subtrees.traverse_map(cls)
        self = super(RootedTree, cls).__new__(cls, subtrees)
        if not all(isinstance(tree, cls) for tree in self.keys()):
            raise TypeError(
                "input must be list of RootedTrees or a LevelSequence")
        return self

    def __bool__(self):
        return True  # All trees have roots, thus aren't empty

    __nonzero__ = __bool__

    def _str(self):
        strings = []
        for subtree in sorted(self.keys(),
                              key=self.__class__.ordered_form,
                              reverse=True):
            # Print tree with multiplicity exponents.
            mult = self[subtree]
            tree_string = subtree._str()
            if mult > 1:
                tree_string += '^%s' % mult
            strings.append(tree_string)
        return '{%s}' % ', '.join(strings)

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
        for tree, mult in self.items():
            level_sequence.extend(tree._ordered_level_sequence(level+1) * mult)
        return level_sequence

    def __len__(self):
        """Number of nodes in the tree."""
        return len(self._ordered_level_sequence())

    def ordered_form(self):
        """Return the dominant representative of the rooted tree."""
        return DominantSequence(self._ordered_level_sequence())


class TreeEnumerator(bases.Enumerable):
    """Represents the class of unlabelled rooted trees on n nodes."""

    def __init__(self, n, _root_height=0):
        if n < 1:
            raise ValueError("Cannot define a rooted tree with %s nodes" % n)
        self.n = n
        self._root_height = _root_height

    def __iter__(self):
        """Generates the dominant representatives of each unordered tree in
        lexicographic order, starting with the tallest tree with level sequence
        range(1, n+1) and ending with [1]+[2]*(n-1).

        Algorithm and description provided in T. Beyer and S. M. Hedetniemi,
        "Constant time generation of rooted trees." Siam Journal of
        Computation, Vol. 9, No. 4. November 1980.
        """
        tree = list(range(self._root_height, self.n+self._root_height))
        yield tuple.__new__(DominantSequence, tree)
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
                yield tuple.__new__(DominantSequence, tree)

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


def forests(n):
    """Enumerate every forest on n nodes."""
    # Any rooted tree on n+1 nodes can be identically described as a
    # collection of rooted trees on n nodes, grafted together at a single
    # root. To enumerate all collections of rooted trees on n nodes, we
    # may enumerate all rooted trees on n+1 nodes, chopping them at the
    # base.
    for tree in TreeEnumerator(n+1):
        yield Multiset(tree.subtrees())
