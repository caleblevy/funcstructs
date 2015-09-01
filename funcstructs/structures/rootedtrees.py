"""Algorithms for representing and enumerating rooted trees.

Caleb Levy, 2014-2015.
"""

from functools import reduce
from itertools import chain, groupby
from math import factorial
from operator import mul

from funcstructs import bases
from funcstructs.combinat import divisors
from funcstructs.utils.subsequences import startswith

from funcstructs.structures.functions import rangefunc
from funcstructs.structures.multiset import Multiset
from funcstructs.structures.labellings import _ordered_divisions

__all__ = "LevelSequence", "DominantSequence", "RootedTree", "TreeEnumerator"


def _levels_from_preim(graph, root=0, keys=None):
    """Return the level sequence of the ordered tree formed such that
    graph[x] are the nodes attached to x.

    Note: The graph must be acyclic, or the function may not terminate.
    """
    # Algorithm for finding an Endofunction's ConjuConjugacyClass taking
    # inspiration from the idea that the preimage of an endofunction
    # is literally the standard representation of a graph as a mapping
    # of its vertices to the set of its edges.
    #
    # The original implementation of this algorithm was recursive,
    # however for functions with trees more than 2000 nodes deep
    # (i.e. sin(x) approximated on 16-bit floats) this would cause
    # a stack overflow, so I moved it to a managed stack.
    #
    # Recursive (and more readable) version was as follows:
    #
    #   def levels(graph, root, level=0):
    #       seq = [level]
    #       for x in graph[root]:
    #           seq.extend(levels(graph, x, level+1))
    #       return seq
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
        # Validity checks:
        # 0) len(self) > 0
        # 1) self[0] == 0
        # 2) all(self[n+1] in range(1, self[n]+2) for n in range(len(self)-1))
        # Note that all nodes must be integers to use them as indices.
        if not self:  # Rule 0
            raise TypeError("a tree must have a root")
        root = previous_node = self[0]
        if not (root == 0 and isinstance(root, int)):  # Rule 1
            raise TypeError("root must have height 0, received %s" % root)
        for node in self[1:]:  # Rule 2
            if not ((1 <= node <= previous_node+1) and isinstance(node, int)):
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
            lim = func.limitset
            if len(lim) != 1:
                raise ValueError("Function structure is not a rooted tree")
            root = next(iter(lim))
        return cls(_levels_from_preim(func.acyclic_ancestors, root))

    def parents(self):
        """Generator of the parent nodes of each node in order."""
        # Algorithm inspired by viewing the ordered level sequence as an
        # implicit function from each node to the most recent node of the next
        # lowest level. By keeping a running record of the most recently
        # visited nodes for each level, we generate the sequence of elements
        # that each node is mapped to.
        grafting_point = [0]*len(self)
        for node, level in enumerate(self):
            yield grafting_point[level-1]
            grafting_point[level] = node

    def children(self):
        """Map of each node to the set of nodes attached to it in order."""
        preim = []
        for node, parent in enumerate(self.parents()):
            preim.append([])
            preim[parent].append(node)
        preim[0].pop(0)
        return preim

    def height_groups(self):
        """Nodes in breadth-first traversal order grouped by height."""
        groups = []
        for node, height in enumerate(self):
            if height+1 > len(groups):
                groups.append([])
            groups[height].append(node)
        return groups

    def breadth_first_traversal(self):
        """Generate nodes in breadth-first traversal order."""
        return chain(*self.height_groups())

    def subtrees(self):
        """Return the subtrees attached to the root."""
        for branch in startswith(self[1:], self[0]+1):
            # Bypass any constructor checks; since the tree is verified,
            # all of its subtrees must be as well.
            yield tuple.__new__(self.__class__, (node-1 for node in branch))

    def traverse_map(self, mapping=list):
        """Apply mapping to the sequence of mapping applied to the subtrees."""
        # The breaking condition here is implicit; if the tree has no subtrees,
        # tree.traverse_map(mapping) is simply not called, returning
        # the equivalent mapping(iter(())).
        return mapping(tree.traverse_map(mapping) for tree in self.subtrees())

    # The following method for converting a rooted tree into canonical form
    # was independently rediscovered by Caleb Levy in Spring 2015. It is
    # featured in
    #
    #   "Canonical forms for labelled trees and their applications in
    #   frequent subtree mining" by UCLA researchers Yun Chi, Yirong Yang and
    #   Richard R. Muntz, published in Knowledge and Infromation Systems in
    #   2005. DOI 10.1007/s10115-004-0180-7.
    #
    # The method runs in O(k*log(k)), with k being the number of nodes in
    # the tree. Essentially, starting at the top, we sort the nodes at
    # each level by using the list of their children as keys (the lists
    # are sorted lexicographically).

    def _node_keys(self, sort=True):
        """Assign to each node a key for sorting"""
        # Leave option to input these to without computing for caching
        parent = list(self.parents())
        node_keys = [0]*len(self)
        child_keys = [[] for _ in self]
        previous_level = []
        sort_value = len(parent)
        for level in reversed(self.height_groups()):
            # enumerate for connections from previous level to current
            for x in previous_level:
                child_keys[parent[x]].append(node_keys[x])
            # Sort nodes of current level lexicographically by the list of
            # their children's keys. Since nodes of the previous level are
            # already sorted, we need not sort the child_keys themselves.
            if sort is True:
                level.sort(key=child_keys.__getitem__, reverse=True)
            # Assign int keys to current level to prevent accumulating nested
            # lists
            for _, run in groupby(level, child_keys.__getitem__):
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
        keys = ot._node_keys()
        level_sequence = _levels_from_preim(ot.children(), 0, keys)
        # No need to run LevelSequence checks; it's either been preordered or
        # treefunc_properties will serve as an effective check due to indexing.
        return super(LevelSequence, cls).__new__(cls, level_sequence)

    def _interchangeable_nodes(self):
        """Groups of interchangeable nodes in BFS order."""
        # TODO: A writeup of this with diagrams will be in the notes.
        # TODO: Given an intuitive explanation of how these two things give
        # different aspects of tree structure: connections and height.
        parents = list(self.parents())
        bft = self.breadth_first_traversal()
        keys = self._node_keys(sort=False)
        # Two nodes are interchangeable iff they have the same key and parent.
        # Interchangeable nodes will always be adjacent in the breadth
        # first traversal of a dominant sequence.
        for _, g in groupby(bft, lambda x: (parents[x], keys[x])):
            yield list(g)

    def degeneracy(self):
        """Number of equivalent representations for each labelling of the
        unordered tree."""
        # Since this degeneracy is a property of *un*-ordered trees, it
        # only makes sense to define it for their *canonical* ordered
        # representatives.
        return reduce(mul, (factorial(len(g))
                            for g in self._interchangeable_nodes()))

    def labellings(self):
        """Enumerate endofunctions with the same tree structure."""
        node_groups = list(self._interchangeable_nodes())
        bin_widths = list(map(len, node_groups))
        translation_sequence = rangefunc(chain(*node_groups)).inverse.conj(
            rangefunc(self.parents()))
        n = len(self)
        func = [0] * n
        for combo in _ordered_divisions(set(range(n)), bin_widths):
            c = list(chain(*combo))
            for i in range(n):
                func[c[i]] = c[translation_sequence[i]]
            yield rangefunc(func)


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

    def __init__(self, n):
        if n < 1 or not isinstance(n, int):
            raise ValueError("Cannot define a rooted tree with %s nodes" % n)
        self.n = n

    def __iter__(self):
        """Generates the dominant representatives of each unordered tree in
        lexicographic order, starting with the tallest tree with level sequence
        range(1, n+1) and ending with [1]+[2]*(n-1).

        Algorithm and description provided in T. Beyer and S. M. Hedetniemi,
        "Constant time generation of rooted trees." Siam Journal of
        Computation, Vol. 9, No. 4. November 1980.
        """
        tree = list(range(self.n))
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

    def __len__(self):
        """Number of trees on n nodes. May break for N >= 25."""
        # Memoize standard sequence for number of rooted trees
        # for every term less than 2**32 (Jython's max index size).
        # We could go to 64-bit (Python and PyPy cutoff), but honestly
        # if someone is going to make a list of > 2 billion trees,
        # the time to do that will dwarf the time to calculate length.
        #
        # Adding a __len__ method will cause PyPy and Python to spit an
        # overflow error when *explicitly* constructing a list of trees
        # on > 50 nodes, as these break the 64 - bit index size limit.
        # This will not break the "for i in TreeEnumerator(n):" syntax,
        # however, which is the only kind I can imagine being used for N
        # > 20 or so (i.e. getting the first few terms or something).
        #
        # As for memoizing magic numbers (instead of the formula):
        # The unit tests (my de facto benchmark) take about 1/2 sec
        # longer just from computing, or about 5%. The problem is
        # that even though the iterator syntax does not *use* the
        # the result of __len__, it still calls it, and
        # there are a lot of (duplicate) rooted trees called when
        # enumerating endofunctions.
        #
        # We keep __len__ here for consistency of interface. As for
        # making the OEIS sequence local to the function: we
        # avoid a global lookup (and this tuple gets translated into
        # LOAD_CONST in bytecode). Making it a tuple further
        # means it is not reconstructed at each call (see
        # "Why is hardcoding this list slower than calculating it?"
        # at http://stackoverflow.com/a/27763902/3349520).
        OEIS_A000081 = (
            1, 1, 2, 4, 9, 20, 48, 115, 286, 719, 1842, 4766,
            12486, 32973, 87811, 235381, 634847, 1721159, 4688676,
            12826228, 35221832, 97055181, 268282855, 743724984,
            2067174645
        )
        return OEIS_A000081[self.n-1] if self.n <= 25 else self.cardinality()

    @bases.typecheck(DominantSequence, RootedTree)
    def __contains__(self, other):
        return len(other) == self.n

    def cardinality(self):
        """Returns the number of rooted tree structures on n nodes. Algorithm
        featured without derivation in Finch, S. R. "Otter's Tree Enumeration
        Constants." Section 5.6 in "Mathematical Constants", Cambridge,
        England: Cambridge University Press, pp. 295-316, 2003."""
        T = [0, 1] + [0]*(self.n - 1)
        for n in range(2, self.n + 1):
            for i in range(1, self.n):
                s = 0
                for d in divisors(i):
                    s += T[d]*d
                s *= T[n-i]
                T[n] += s
            T[n] //= n-1
        return T[-1]
