"""Honing of lazy tree function evaluation with a sane interface.

Caleb Levy, 2015.
"""

from __future__ import print_function
from collections import defaultdict


def _graph_tree(graph, root=0, keys=None):
    """Return the level sequence of the ordered tree formed such that graph[x]
    are the nodes attached to x."""
    if keys is not None:
        graph = [sorted(attachments, key=keys.get) for attachments in graph]
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


def _func_tree(func, root=None):
    """Return function level iterator"""
    if root is None:
        root = next(iter(func.limitset))
        if len(func.limitset) != 1:
            raise ValueError("Function structure is not a rooted tree")
    for level in _graph_tree(func.acyclic_ancestors, root):
        yield level


def _tree_properties(levels):
    """Return an endofunction corresponding to a sequence of levels"""
    levels = iter(levels)
    root = height_prev = next(levels)

    level_sequence = [root]
    height_groups = defaultdict(list)
    height_groups[0].append(0)
    func = [0]
    preim = defaultdict(set)
    for node, height in enumerate(levels, start=1):
        level_sequence.append(height)
        if height > height_prev:
            func.append(height_groups[height_prev-root][-1])
            height_prev += 1
        else:
            func.append(height_groups[height-root-1][-1])
            height_prev = height
        preim[func[-1]].add(node)
        height_groups[height-root].append(node)
    return func, preim, height_groups


print(_tree_properties([1, 2, 3, 4, 5]))
print()
print(_tree_properties(iter([0, 1, 2, 2, 3, 3, 3, 4, 5, 5, 4, 3, 3, 2, 1, 2])))
