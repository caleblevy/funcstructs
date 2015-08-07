"""Benchmarking Funcstruct methods on large Endofunctions.

When Funcstruct was naively implemented using O(n^2) methods, inputs
with >2000 nodes were infeasible to work with. Right now we can handle
~10**6 nodes in seconds. These gains were hard won, and we don't want
to let regressions slip through.
"""

from __future__ import print_function

from funcstructs.prototypes.timing import Stopwatch
from funcstructs import *

with Stopwatch() as r:
    f = randfunc(10**6)
    r.lap()
    g = randfunc(10**6)
    r.lap()
    h = randfunc(10**6)
    r.lap()

print("Endofunction creation:", r.laps)


with Stopwatch() as s:
    F = Funcstruct(f)
    s.lap()
    G = Funcstruct(g)
    s.lap()
    H = Funcstruct(h)
    s.lap()

print("Funcstruct creation:", s.laps)


with Stopwatch() as t:
    a = F.degeneracy()
    t.lap()
    b = G.degeneracy()
    t.lap()
    c = H.degeneracy()
    t.lap()

print("Funcstruct degeneracies:", t.laps)
