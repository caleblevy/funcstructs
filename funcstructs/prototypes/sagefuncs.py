import os
import time
from collections import defaultdict

import sage.all as sage

from funcstructs import *


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


def iterate(G):
    """Compose a DiGraph with itself."""
    d = defaultdict(set)
    for v in G:
        for e in G.neighbors_out(v):
            d[v].update(G.neighbors_out(e))
    return sage.DiGraph(d)


def compose(F, G):
    """Compose graphs by edge substitution"""
    d = {}
    for v in G:
        d[v] = set()
        for e in G.neighbors_out(v):
            d[v].update(F.neighbors_out(e))
    return sage.DiGraph(d)


def fold(*digraphs):
    """Compose a list of digraphs associatively."""
    return reduce(compose, digraphs)


f = Function({4: 8, 8: 3, 3: 0, 0: 2, 2: 0, 6: 0, 9: 0, 7: 5, 5: 7, 1: 5})
g = fgraph(f)
scriptplot(g)
scriptplot(iterate(g))
scriptplot(fgraph(f**2))

F = sage.digraphs.RandomDirectedGNC(10)
G = sage.digraphs.RandomDirectedGNC(10)
H = sage.digraphs.RandomDirectedGNC(10)
print(iterate(G) == compose(G, G))
print(compose(F, G) == compose(G, F))
print(compose(F, G) == compose(G, H))
print(compose(compose(F, G), H) == compose(F, compose(G, H)) == fold(F, G, H))
scriptplot(F)
scriptplot(G)
scriptplot(H)
scriptplot(compose(F, G))
scriptplot(compose(G, H))
scriptplot(compose(compose(F, G), H))
scriptplot(compose(F, compose(G, H)))
scriptplot(fold(F, G, H))
