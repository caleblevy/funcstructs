"""Honing of lazy tree function evaluation with a sane interface.

Caleb Levy, 2015.
"""

from collections import defaultdict


def levels_from_preim(graph, root=0, keys=None):
    """Return the level sequence of the ordered tree formed such that graph[x]
    are the nodes attached to x."""
    if keys is not None:
        for x in graph:
            graph[x].sort(key=keys.__getitem__)
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


def funclevels_iterator(levels):
    """Lazily generate the function of a level tree and each node's level"""
    levels = iter(levels)
    root = previous_level = next(levels)
    f = node = 0
    yield node, 0, f  # node, normalized height, and what it's mapped to
    grafting_point = {0: 0}
    for node, level in enumerate(levels, start=1):
        if level > previous_level:
            f = grafting_point[previous_level-root]
            previous_level += 1
        else:
            f = grafting_point[level-root-1]
            previous_level = level
        yield node, level-root, f
        grafting_point[level-root] = node


def treefunc_properties(levels):
    """Given an ordered tree's level sequence, return an endofunction with the
    tree's structure, that functions preimage, and the nodes of that tree in
    breadth-first traversal order grouped by height."""
    func = []
    hg = [[]]
    preim = defaultdict(list)
    for n, l, f in funclevels_iterator(levels):
        func.append(f)
        preim[f].append(n)
        if l >= len(hg):
            hg.append([])
        hg[l].append(n)
    preim[0].pop(0)  # Remove 0 to prevent infinite loop in levels_from_preim
    return func, preim, hg
