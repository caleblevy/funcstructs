"""Extra timing functions not found in timeit.

Caleb Levy, 2015.
"""

from __future__ import print_function

import gc
import contextlib
from time import time

from numpy import log2
import matplotlib.pyplot as plt

from endofunction_structures import *
from endofunction_structures.productrange import parse_ranges


show = plt.show


@contextlib.contextmanager
def gcoff():
    """Turn of garbage collection inside the block"""
    gc.disable()
    try:
        yield
    finally:
        gc.enable()


def _call_string(*args, **kwargs):
    """Return format of args and kwargs as viewed when typed out"""
    arg_strings = []
    for arg in args:
        arg_strings.append(repr(arg))
    for key, arg in kwargs.items():
        arg_strings.append(key+'='+repr(arg))
    return "(%s)" % ', '.join(arg_strings)


def _object_name(ob):
    """Return name of ob."""
    try:
        return ob.__name__
    except AttributeError:
        return ob.__class__.__name__


def iteration_time(gen, *args, **kwargs):
    """Time to exhaust gen. If gen is callable, time gen(*args, **kwargs)."""
    printing = kwargs.pop('printing', True)
    call_sig = _object_name(gen)
    if callable(gen):
        gen = gen(*args, **kwargs)
        call_sig += _call_string(*args, **kwargs)
    with gcoff():
        ts = time()
        for i, el in enumerate(gen, start=1):
            pass
        tf = time()
    tot = tf - ts
    if printing:
        print("Enumerated %s items from %s in %s seconds" % (i, call_sig, tot))
    return tot


def _map_setup_call_sig(mapfunc, setupfunc):
    call_sig = _object_name(mapfunc) + "(%s)"
    if setupfunc is not None:
        call_sig %= _object_name(setupfunc) + "(%s)"
    return call_sig


def mapping_time(gen, mapfunc, setupfunc=None, printing=True):
    """Array of times to apply mapfuc to each element in gen."""
    map_times = []
    call_sig = _map_setup_call_sig(mapfunc, setupfunc)
    with gcoff():
        for el in gen:
            ob = el if setupfunc is None else setupfunc(el)
            ts = time()
            mapfunc(ob)
            tf = time()
            tim = tf - ts
            if printing:
                print("%s: %s seconds" % (call_sig % el, tim))
            map_times.append(tim)
    return map_times


def _split_ranges_from_funcs(args):
    """Extract numbers from args, turn them into range, return list of rest"""
    ranges = []
    args = list(reversed(args))
    while args:
        arg = args.pop()
        if not isinstance(arg, (int, type(None))):
            break
        if arg:
            ranges.append(arg)
    ranges[0] += 1
    if len(ranges) > 1:
        ranges[1] += 1
    return range(*ranges), [arg] + list(reversed(args))


def _unpack_mapfuncs(funcs):
    """If a func in funcs is not paired with setup, return pair with None"""
    for func in funcs:
        if callable(func):
            yield func, None
        else:
            yield func


def mapping_plots(*args, **kwargs):
    """Plots of everything in mapfuncs"""
    plotrange, funcs = _split_ranges_from_funcs(args)
    printing = kwargs.pop('printing', False)
    plotfuncs = []
    for func in _unpack_mapfuncs(funcs):
        mapfunc, setupfunc = func
        call_sig = _map_setup_call_sig(mapfunc, setupfunc)
        plotfuncs.append((mapfunc, setupfunc, call_sig))
    plt.figure()
    plt.xlabel('n')
    for mapfunc, setupfunc, call_sig in plotfuncs:
        plt.plot(
            plotrange,
            mapping_time(plotrange, mapfunc, setupfunc, printing),
            label=call_sig % 'n'
        )
    plt.legend(loc='upper left')
    plt.draw()


def flattree(n):
    """Tree with all non-root nodes connected directly to root"""
    return Endofunction([0]*n)


def identity(n):
    """Endofunction corresponding to f[x] == x for x in f.domain"""
    return Endofunction(range(n))


def talltree(n):
    """Endofunction with f[0] == 0 and f[n] == n-1 for n in f.domain"""
    return Endofunction([0] + list(range(n)))


def bigcycle(n):
    """Cyclic permutation of range(n)"""
    return Endofunction(list(range(1, n)) + [0])


def balanced_binary_tree(n):
    """Produce a balanced binary tree of height n."""
    h = int(log2(n)) + 1
    tree = [h]
    while h-1:
        h -= 1
        tree *= 2
        tree = [h] + tree
    return Endofunction.from_tree(OrderedTree(tree))


def scattered_tree(n):
    """Tree with a big cycle and things attached"""
    return Endofunction(list(bigcycle(n//2))+list(talltree(n-n//2)))


if __name__ == '__main__':
    iteration_time(levypartitions.fixed_lex_partitions(100, 40))
    iteration_time(EndofunctionStructures(12))
    iteration_time(EndofunctionStructures, 12)
    iteration_time(PartitionForests, [2, 2, 3, 5])
    iteration_time(productrange.productrange, -2, [2, 2, 2, 3, 5], step=2)

    mapping_time(range(1, 2000), Endofunction.cycles.fget, flattree)
    mapping_time(range(1, 2000), sum, range)
    mapping_time(range(1, 2000), range)

    mapping_plots(2000, (sum, range), range, printing=True)
    mapping_plots(
        20, 2000,
        (Endofunction.cycles.fget, randfunc),
        (periodicity, randfunc),
        printing=True
    )

    mapping_plots(
        20, 2500,
        (Endofunction.cycles.fget, randfunc),
        (Endofunction.cycles.fget, identity),
        (Endofunction.cycles.fget, randperm),
        (Endofunction.cycles.fget, talltree),
        (Endofunction.cycles.fget, balanced_binary_tree),
        (Endofunction.cycles.fget, bigcycle),
        (Endofunction.cycles.fget, scattered_tree),
        printing=True
    )
    plt.show()
