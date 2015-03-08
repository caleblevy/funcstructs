#!/usr/bin/env python
# Copyright (C) 2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.

from sage.all import *

from endofunction_structures import rootedtrees, endofunctions


def tree_to_graph(tree):
    """ Return the graphical form of a rooted tree. """
    f = endofunctions.Endofunction(tree).attached_treenodes
    labels = {node: list(neighbors) for node, neighbors in enumerate(f)}
    g = Graph(labels)
    return g


def levseq_to_graph(seq):
    """ Return the graph of the level sequence corresponding to a rooted tree.
    """
    return tree_to_graph(rootedtrees.DominantTree(seq))


def tree_plot(g, name='tree'):
    """Plot a rooted tree, and return the positions"""
    p = g.plot(
        layout='tree',
        tree_root=0,
        save_pos=True,
        vertex_labels=False,
        tree_orientation='up'
    )
    p.save(name+'.pdf')


if __name__ == '__main__':
    l1 = [1, 2, 3, 4, 4, 4, 3, 3, 2, 3, 3, 2]
    l2 = [1, 2, 3, 4, 4, 3, 4, 4, 2, 3, 4, 4, 3, 4, 4]
    g1 = levseq_to_graph(l1)
    g2 = levseq_to_graph(l2)
    tree_plot(g1)
    tree_plot(g2, 'binary')
