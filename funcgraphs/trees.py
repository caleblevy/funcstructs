#!/usr/bin/env python
# Copyright (C) 2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.

from sage.all import *

from endofunction_structures import rootedtrees, endofunctions
from . import connections


def _place_tree_nodes(tree, name=None):
    """ Save basic tree plot or return node positions depending on calling
    wrapper. """
    t = rootedtrees.DominantTree(tree)
    f = endofunctions.Endofunction(t).attached_treenodes
    labels = {node: list(neighbors) for node, neighbors in enumerate(f)}
    g = Graph(labels)
    gp = g.graphplot(
        layout='tree',
        tree_root=0,
        save_pos=True,
        vertex_labels=False,
        tree_orientation='up'
    )
    if name is not None:
        gp.plot().save('funcgraphs/images/'+name+'.pdf')
    else:
        return g.get_pos()


def tree_plot(tree, name):
    """Plot a rooted tree, and return the positions"""
    _place_tree_nodes(tree, name)


def treenode_positions(tree):
    """Return node placements of the rooted tree. """
    return _place_tree_nodes(tree)


def rooted_tree_plot(tree, name, downarrows=False):
    """Make rooted tree plot with root loop and downward arrows optionally."""
    tree_pos = treenode_positions(tree)
    f = endofunctions.Endofunction(rootedtrees.DominantTree(tree))
    if downarrows:
        dg = DiGraph(connections.func_to_vertices(f))
    else:
        dg = Graph(connections.func_to_vertices(f))
    dgp = dg.graphplot(vertex_labels=False)
    for node, loc in tree_pos.items():
        dgp._pos[node] = loc
    dgp.set_vertices()
    dgp.set_edges()
    dp = dgp.plot()
    if name is not None:
        dp.save('funcgraphs/images/'+name+'.pdf')


if __name__ == '__main__':
    l1 = [1, 2, 3, 4, 4, 4, 3, 3, 2, 3, 3, 2]
    l2 = [1, 2, 3, 4, 4, 3, 4, 4, 2, 3, 4, 4, 3, 4, 4]
    tree_plot(l1, 'tree')
    tree_plot(l2, 'binary')
    rooted_tree_plot(l1, 'downtree', downarrows=True)
    tree_plot([1]+[2]*100+[3]*100, 'onebig')
