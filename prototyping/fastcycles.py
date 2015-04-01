# Copyright (C) 2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.

"""Testing module for developing an O(n) implementation of a function cycle
enumerator."""


from endofunction_structures import *

import time
import matplotlib.pyplot as plt

ef = randfunc(10000)


def fastcycles(f):
    """Proof of concept for finding the path cycles in linear time."""
    Tried = set()
    CycleEls = set()
    Remaining = set(range(len(f)))
    while Remaining:
        x = Remaining.pop()
        path = [x]
        while x not in Tried:
            Remaining.discard(x)
            Tried.add(x)
            x = f[x]
            path.append(x)
        if x not in CycleEls:
            cycle = path[path.index(x)+1:]
            if cycle:
                print cycle
                CycleEls.update(cycle)
    return CycleEls


f = Endofunction(SymmetricFunction([(0, 1, 2), (3, 4), (5, 6)]))
print f
fastcycles(f)
print
h = Endofunction(list(f)+[0])
fastcycles(h)

g = randfunc(100)
for c in g.cycles:
    print c
fastcycles(g)


if __name__ == '__main__':
    fast_times = []
    slow_times = []
    for p in range(1, 2000):
        f = randfunc(p)
        ts = time.time()
        l = fastcycles(f)
        fast_times.append(time.time()-ts)
        ts = time.time()
        f.cycles
        slow_times.append(time.time()-ts)
        print len(f.cycles)
        print f.limitset - l
        print l - f.limitset

    p1 = plt.plot(fast_times, label='func')
    p2 = plt.plot(slow_times, label='method')
    plt.legend(loc='upper left')
    plt.show()
