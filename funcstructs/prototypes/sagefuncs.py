import os
import time
import unittest
from collections import defaultdict

import sage.all as sage

from funcstructs import *
from funcstructs.structures.functions import _parsed_domain


def fgraph(f):
    """Return the DiGraph of the graph f."""
    return sage.DiGraph({x: [y] for x, y in f})


def randf(*args, **kwargs):
    """Return the DiGraph of a random function on a domain."""
    return fgraph(randfunc(*args, **kwargs))


def scriptplot(G):
    """Plot graph of G in a script"""
    plots = [p for p in os.listdir('.') if p.startswith("plot") and
             p.endswith(".png")]
    plots = [p[4:-4] for p in plots]
    plot_numbers = [0]
    for p in plots:
        # Note to self: must get rid of habit of writing piss-poor parser
        # every time I need to get a file name.
        try:
            n = abs(int(p))
        except (TypeError, ValueError):
            n = 0
        plot_numbers.append(n)
    plot_number = max(plot_numbers) + 1  # this really sucks...
    plot_name = "plot" + str(plot_number) + ".png"
    G.plot().save(plot_name)
    os.system("open -a Preview " + plot_name)


def _compose(F, G):
    """Compose graphs by edge substitution"""
    d = {}
    for v in G:
        d[v] = set()
        for e in G.neighbors_out(v):
            d[v].update(F.neighbors_out(e))
    return sage.DiGraph(d)


def compose(*digraphs):
    """Compose a list of digraphs associatively."""
    return reduce(_compose, digraphs)


def identity(vertices):
    """Return the identity graph on vertex set V."""
    return sage.DiGraph({v: [v] for v in _parsed_domain(vertices)})


def iterate(G, n):
    """Iterate a general graph to n compositions with itself."""
    G_iter = identity(G)
    for it in bin(n)[-1:1:-1]:
        if it == '1':
            G_iter = compose(G, G_iter)
        G = compose(G, G)
    return G_iter


class GraphCompositionTests(unittest.TestCase):

    def test_iteration(self):
        """Test graph composition generalizes function composition and
        preserves associativity."""
        f = rangefunc([2, 5, 0, 0, 8, 7, 0, 5, 3, 0])
        g = fgraph(f)
        self.assertEqual(compose(g, g), fgraph(f*f))
        for i in range(20):
            self.assertEqual(iterate(g, i), fgraph(f**i))
        # test special case associativity
        self.assertEqual(compose(iterate(g, 4), iterate(g, 3)), fgraph(f**7))

    def test_composition(self):
        """Test composition is associative and not commutative with know
        graphs."""
        F = sage.digraphs.RandomDirectedGNC(10)
        G = sage.digraphs.RandomDirectedGNC(10)
        H = sage.digraphs.RandomDirectedGNC(10)
        self.assertEqual(compose(iterate(G, 3), iterate(G, 4)), iterate(G, 7))
        self.assertEqual(compose(F, compose(G, H)), compose(compose(F, G), H))
        self.assertEqual(compose(F, compose(G, H)), compose(F, G, H))


G = sage.DiGraph({
    1: [2, 8],
    2: [3],
    3: [4],
    4: [5, 1],
    5: [6],
    6: [7],
    7: [5, 8],
    8: [9],
    9: [10],
    10: [11],
    11: [8]
})

print(G.strongly_connected_components())
print(iterate(G, 2).strongly_connected_components())

if __name__ == '__main__':
    unittest.main()
