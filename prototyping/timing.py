# Copyright (C) 2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.

"""Extra timing functions not found in timeit."""

from __future__ import print_function

from time import time

import matplotlib.pyplot as plt

from endofunction_structures.productrange import parse_ranges


def call_string(*args, **kwargs):
    """Return format of args and kwargs as viewed when typed out"""
    arg_strings = []
    for arg in args:
        arg_strings.append(repr(arg))
    for key, arg in kwargs.items():
        arg_strings.append(key+'='+repr(arg))
    return "(%s)" % ', '.join(arg_strings)


def object_name(ob):
    """Return name of ob."""
    try:
        return ob.__name__
    except AttributeError:
        return ob.__class__.__name__


def iteration_time(gen, *args, **kwargs):
    """Time to exhaust gen. If gen is callable, time gen(*args, **kwargs)."""
    printing = kwargs.pop('printing', True)
    call_sig = object_name(gen)
    if callable(gen):
        gen = gen(*args, **kwargs)
        call_sig += call_string(*args, **kwargs)
    ts = time()
    for i, el in enumerate(gen, start=1):
        pass
    tf = time()
    tot = tf - ts
    if printing:
        print("Enumerated %s items from %s in %s seconds" % (i, call_sig, tot))
    return tot


def _map_setup_call_sig(mapfunc, setupfunc):
    call_sig = object_name(mapfunc) + "(%s)"
    if setupfunc is not None:
        call_sig %= object_name(setupfunc) + "(%s)"
    return call_sig


def mapping_time(gen, mapfunc, setupfunc=None, printing=True):
    """Array of times to apply mapfuc to each element in gen."""
    map_times = []
    call_sig = _map_setup_call_sig(mapfunc, setupfunc)
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
        if not isinstance(arg, int):
            break
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
    ax = plt.gca()
    plt.xlabel('n')
    for mapfunc, setupfunc, call_sig in plotfuncs:
        plt.plot(
            plotrange,
            mapping_time(plotrange, mapfunc, setupfunc, printing),
            label=call_sig % 'n'
        )
    plt.legend(loc='upper left')
    plt.show()


if __name__ == '__main__':
    from endofunction_structures import *
    iteration_time(levypartitions.fixed_lex_partitions(100, 40))
    iteration_time(EndofunctionStructures(12))
    iteration_time(EndofunctionStructures, 12)
    iteration_time(PartitionForests, [2, 2, 3, 5])
    iteration_time(productrange.productrange, -2, [2, 2, 2, 3, 5], step=2)

    def flattree(n): return Endofunction([0]*n)

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

    def identity(n): return Endofunction(range(n))

    mapping_plots(
        20, 2000,
        (Endofunction.cycles.fget, randfunc),
        (Endofunction.cycles.fget, identity),
        (Endofunction.cycles.fget, randperm),
        printing=True
    )
