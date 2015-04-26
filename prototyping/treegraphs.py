"""Caleb Levy, 2015."""
from sage.all import *

import numpy as np

from endofunction_structures import rootedtrees, endofunctions
from funcgraphs import coordinates
from . import connections


class TreeGraph(rootedtrees.DominantTree):

    def func_form(self):
        """Return a function form of the tree"""
        return endofunctions.Endofunction(self)

    def sage_graph(self):
        """Return sage graph of tree so that self.is_tree() returns true"""
        connections = {}
        for node, neighbors in enumerate(self.func_form().attached_treenodes):
            connections[node] = list(neighbors)
        return Graph(connections)

    def _place_tree_nodes(self, name=None):
        """Save basic tree plot or return node positions depending on calling
        wrapper."""
        g = self.sage_graph()
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

    def sage_plot(self, name):
        """Plot the rooted tree using sage defaults"""
        self._place_tree_nodes(name)

    def sage_node_positions(self):
        """Return node placements of the rooted tree. """
        return self._place_tree_nodes()

    def directed_sage_plot(self, name, downarrows=False):
        """Make rooted tree plot with root loop and downward arrows
        optionally."""
        tree_pos = self.sage_node_positions()
        f = self.func_form()
        gfunc = Graph
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

    def sage_node_coordinates(self):
        """Coordinate object representing positions of the tree nodes."""
        t = self.sage_node_positions()
        z = map(coordinates.Point, [t[i] for i in range(len(self))])
        coords = coordinates.Coordinates(z)
        return coords - coords[0]

    def vertical_offsets(self):
        """Locations scaled """
        pass


def balanced_binary_tree(n):
    """Produce a balanced binary tree of height n."""
    h = n
    tree = [h]
    while h-1:
        h -= 1
        tree *= 2
        tree = [h] + tree
    return TreeGraph(tree)


if __name__ == '__main__':
    l1 = TreeGraph([1, 2, 3, 4, 4, 4, 3, 3, 2, 3, 3, 2])
    l2 = TreeGraph([1, 2, 3, 4, 4, 3, 4, 4, 2, 3, 4, 4, 3, 4, 4])
    l1.sage_plot('tree')
    l2.sage_plot('binary')
    l1.directed_sage_plot('downtree', downarrows=True)
    l3 = TreeGraph([1]+[2]*100+[3]*100)
    l3.sage_plot('onebig')
    print l3.sage_node_coordinates().z
    print TreeGraph(range(100)).sage_node_coordinates().z
    t4 = [1, 2, 3, 4, 4, 3, 4, 4, 2, 3, 4, 5, 4, 5, 3, 4, 4, 2, 3, 4, 5, 5]
    l4 = TreeGraph(t4)
    l4.sage_plot('hi')
    balanced_binary_tree(6).sage_plot('fractal')
