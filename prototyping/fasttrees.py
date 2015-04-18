"""Development of fast, nonrecursive algorithm for computing the structure of
an endofunction.

Caleb Levy, 2015.
"""

from __future__ import print_function

from endofunction_structures import *

from .timing import *


def node_levels(func, y=5):
    """Return the levels of all nodes in the subtree attached to y"""
    preim = {y}
    level = 1
    level_map = {y: level}
    while preim:
        level += 1
        nextim = set()
        for x in preim:
            nextim.update(func.attached_treenodes[x])
        level_map.update({node: level for node in nextim})
        preim = set(nextim)
    return level_map


def tree_sequence(func, x):
    """Return the level sequence of the tree attached to x from func"""
    level_map = node_levels(func, x)
    node_stack = [x]
    level_sequence = []
    while node_stack:
        x = node_stack.pop()
        level_sequence.append(level_map[x])
        node_stack.extend(func.attached_treenodes[x])
    return level_sequence


if __name__ == '__main__':
    t = DominantTree([1, 2, 3, 4, 5, 2, 3, 4, 3])
    f = Endofunction([i-1 for i in [5, 4, 6, 6, 4, 6, 9, 3, 8]])
    l = node_levels(f)
    print(f.tree_form() == t)
    print('\nlevels:')
    for i in range(len(f)):
        print(i, ':', l[i])
    print(tree_sequence(f, 5))
    g = randfunc(10000)
    for x in g.limitset:
        h = DominantTree(tree_sequence(g, x))
        k = DominantTree(g._attached_level_sequence(x))
        if h != k:
            raise Exception("Wah, it didn't work!")

    def cached_func(n):
        f = randfunc(n)
        f.cycles
        f.limitset
        f.preimage
        f.attached_treenodes
        return f

    def stack_tree(f):
        for x in f.limitset:
            tree_sequence(f, x)

    def rec_tree(f):
        for x in f.limitset:
            f._attached_level_sequence(x)

    mapping_plots(
        4000,
        (stack_tree, cached_func),
        (rec_tree, cached_func),
        printing=True
    )
    import matplotlib.pyplot as plt
    plt.show()
