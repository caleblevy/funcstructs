# Copyright (C) 2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.

"""Extra timing functions not found in timeit."""

from __future__ import print_function

from time import time


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


if __name__ == '__main__':
    from endofunction_structures import *
    iteration_time(levypartitions.fixed_lex_partitions(100, 40))
    iteration_time(EndofunctionStructures(12))
    iteration_time(EndofunctionStructures, 12)
    iteration_time(PartitionForests, [2,2,3,5])
    iteration_time(productrange.productrange, -2, [2, 2, 2, 3, 5], step=2)
