"""Benchmarking Funcstruct methods on large Endofunctions.

When Funcstruct was naively implemented using O(n^2) methods, inputs
with >2000 nodes were infeasible to work with. Right now we can handle
~10**6 nodes in seconds. These gains were hard won, and we don't want
to let regressions slip through.
"""

from __future__ import print_function

import numpy as np

from funcstructs.prototypes.timing import Stopwatch
from funcstructs.prototypes.floatfuncs import *
from funcstructs.structures import *


with Stopwatch() as u:
    square = floatfunc(lambda x: x*x, NonNegative)
    u.lap()
    sine = floatfunc(np.sin)
    u.lap()

print("Making floating point Endofunctions:", u.laps)


with Stopwatch() as v:
    Square = Funcstruct(square)
    v.lap()
    Sine = Funcstruct(sine)
    v.lap()

print("Floating point Funcstructs:", v.laps)


with Stopwatch() as w:
    d = Square.degeneracy()
    w.lap()
    e = Sine.degeneracy()
    w.lap()

print("Floating point degeneracy:", w.laps)


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
