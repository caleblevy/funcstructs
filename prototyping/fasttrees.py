"""Development of fast, nonrecursive algorithm for computing the structure of
an endofunction.

Caleb Levy, 2015.
"""

from __future__ import print_function

import collections
import unittest

from endofunction_structures import *
from .timing import *


def node_levels(func, x, ordered=False):
    """Return the levels of all nodes in the subtree attached to x"""
    node_queue = collections.deque([x])
    jump_node = x
    level_map = {} if not ordered else collections.OrderedDict()
    level = 1
    while node_queue:
        x = node_queue.popleft()
        level_map[x] = level
        node_queue.extend(func.attached_treenodes[x])
        if x == jump_node and node_queue:
            level += 1
            jump_node = node_queue[-1]
    return level_map


def nodekeys(func, node):
    level_map = node_levels(func, node, ordered=True)
    node_keys = collections.defaultdict(list)  # sorting key assigned to nodes
    levels = subsequences.runs(
        reversed(list(level_map.keys())),
        lambda x, y: level_map[x] == level_map[y]  # break at level change
    )
    previous_level = next(levels)
    # sort_value will decrease to produce dominant tree
    sort_value = 1
    for x in previous_level:
        node_keys[x] = sort_value  # Top ones all look identical
    # NOTE: node_keys[node] <==> sorting key for that node
    for level in levels:
        # Account for connections from previous level to current
        for x in previous_level:
            node_keys[func[x]].append(node_keys[x])
        # Sort nodes of current level by weight of their connections
        for y in level:
            node_keys[y].sort(reverse=True)
        # Make a sorted list copy, since iteration order matters
        sorted_nodes = sorted(level, key=node_keys.get)
        # Make copy of sorting keys; they will be overwritten in the loop
        sorting_keys = list(map(node_keys.get, sorted_nodes))
        # Overwrite sorting keys to prevent accumulation of nested lists
        for run in subsequences.runs(
                    zip(sorted_nodes, sorting_keys),
                    lambda x, y: x[1] == y[1]):
            sort_value += 1
            for x in run:
                node_keys[x[0]] = sort_value
        previous_level = level
    return node_keys


def attached_treenodes(func, x, node_keys=False):
    if not node_keys:
        return func.attached_treenodes[x]
    else:
        return sorted(func.attached_treenodes[x], key=node_keys.get)


def tree_sequence(func, x, _node_keys=False):
    """Return the level sequence of the tree attached to x from func"""
    level_map = node_levels(func, x)
    node_stack = [x]
    level_sequence = []
    while node_stack:
        x = node_stack.pop()
        level_sequence.append(level_map[x])
        node_stack.extend(attached_treenodes(func, x, _node_keys))
    return level_sequence


def sorted_tree_sequence(func, x):
    return tree_sequence(func, x, _node_keys=nodekeys(func, x))


class TestTreeSequences(unittest.TestCase):

    def test_sequences(self):
        g = randfunc(100)
        for x in g.limitset:
            self.assertEqual(
                g.attached_tree(x),
                DominantTree(tree_sequence(g, x))
            )
        t = DominantTree([1, 2, 3, 4, 5, 2, 3, 4, 3])
        f = Endofunction(Endofunction([4, 3, 5, 5, 3, 5, 8, 2, 7]))
        l = DominantTree(tree_sequence(f, 5))
        self.assertEqual(t, l)

    def test_sorting(self):
        t = DominantTree([1, 2, 3, 4, 5, 2, 3, 4, 3])
        f = Endofunction(Endofunction([4, 3, 5, 5, 3, 5, 8, 2, 7]))
        lsort = OrderedTree(sorted_tree_sequence(f, 5))
        self.assertEqual(t, lsort)
        g = randfunc(100)
        for x in g.limitset:
            # First ensure same tree structure
            self.assertEqual(
                g.attached_tree(x),
                DominantTree(sorted_tree_sequence(g, x))
            )
            # Check that the ordering is the same
            self.assertEqual(
                g.attached_tree(x),
                OrderedTree(sorted_tree_sequence(g, x))
            )


def cached_func(n):
    f = randfunc(n)
    f.cycles
    f.limitset
    f.preimage
    f.attached_treenodes
    return f


def conversion_times(start, stop=None, step=None):

    def level_tree(f):
        for x in f.limitset:
            node_levels(f, x)

    def stack_tree(f):
        for x in f.limitset:
            tree_sequence(f, x)

    def rec_tree(f):
        for x in f.limitset:
            f._attached_level_sequence(x)

    mapping_plots(
        start, stop, step,
        (stack_tree, cached_func),
        (rec_tree, cached_func),
        (level_tree, cached_func),
        printing=True
    )
    show()


def ordering_times(start, stop=None, step=None):

    def recursive_order(f):
        for x in f.limitset:
            f.attached_tree(x)

    def stack_order(f):
        for x in f.limitset:
            sorted_tree_sequence(f, x)

    mapping_plots(
        start, stop, step,
        (recursive_order, talltree),
        (stack_order, talltree),
        (recursive_order, randfunc),
        (stack_order, randfunc),
        printing=True
    )

    show()


if __name__ == '__main__':
    conversion_times(3000)
    ordering_times(500)
    unittest.main()
