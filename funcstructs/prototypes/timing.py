from __future__ import print_function

import gc
from timeit import default_timer

import matplotlib.pyplot as plt
from numpy import log2

from funcstructs.structures import *
from funcstructs.utils.productrange import productrange
from funcstructs.prototypes.integer_partitions import fixed_lex_partitions


class Stopwatch(object):
    """A timer as a context manager.

    Wraps around a timer. A custom timer can be passed to the
    constructor. The default timer is timeit.default_timer. The garbage
    collector is disabled during timings by default.

    Laps can be recorded using the the "lap" method. When first called,
    it records the total elapsed time. Subsequent calls append time
    since the previous lap.

    Usage:

    >>> with Timer(factor=1000) as t:
    ...     # do some things
    ...     print t.elapsed
    ...     # do other tings
    ...     t.lap()
    ...     # do yet more
    ...     t.lap()
    ...
    10.122  # in ms
    >>> print t.laps, t.elapsed
    (20.567, 5.136), 25.703
    """

    def __init__(self, gcoff=True, timer=default_timer, factor=1):
        self._timer = timer
        self._factor = factor
        self._end = None
        self._lap = 0
        self._laps = []
        self._gcoff = gcoff

    def __call__(self):
        """Return the current time"""
        return self._timer()

    def __enter__(self):
        """Set the start time."""
        if self._gcoff:
            gc.disable()
        self._start = self()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """Set the end time."""
        self._end = self()
        gc.enable()

    def __str__(self):
        return '%.3f' % self.elapsed

    @property
    def elapsed(self):
        """Return the current elapsed time since start

        If the `elapsed` property is called in the context manager scope,
        the elapsed time bewteen start and property access is returned.
        However, if it is accessed outside of the context manager scope,
        it returns the elapsed time bewteen entering and exiting the scope.

        The `elapsed` property can thus be accessed at different points within
        the context manager scope, to time different parts of the block.
        """
        if self._end is None:
            # if elapsed is called in the context manager scope
            return (self() - self._start) * self._factor
        else:
            # if elapsed is called out of the context manager scope
            return (self._end - self._start) * self._factor

    def lap(self):
        """Mark start of new lap."""
        if self._end is None:
            self._laps.append(self.elapsed - self._lap)
            self._lap = self.elapsed
        else:
            raise RuntimeError("Stopwatch not running")

    @property
    def laps(self):
        """Return laps recorded during the timing."""
        return tuple(self._laps)

    def reset(self):
        """Reset the timer and all laps."""
        if self._end is None:
            self._lap = 0
            self._laps = []
            self._start = self()
        else:
            raise RuntimeError("Cannot reset finished Timer")


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
    with Stopwatch() as t:
        for i, el in enumerate(gen, start=1):
            pass
    if printing:
        print("Enumerated %s items from %s in %s seconds" % (i, call_sig, t))
    return t.elapsed


def maptime(gen, mapfunc, setupfunc=None):
    """Array of times to apply mapfuc to each element in gen."""
    gen = list(map((lambda el: el) if setupfunc is None else setupfunc, gen))
    with Stopwatch() as t:
        for el in gen:
            mapfunc(el)
            t.lap()
    return t.laps


def _map_setup_call_sig(mapfunc, setupfunc):
    """Call string for callable and """
    call_sig = _object_name(mapfunc) + "(%s)"
    if setupfunc is not None:
        call_sig %= _object_name(setupfunc) + "(%s)"
    return call_sig


def mapbench(gen, mapfunc, *setupfuncs):
    """Comparison plot of mapfuncs applied to gen. A mapfunc may either be a
    callable or a tuple-pair of callables, one being the mapping, and the other
    being the setup function."""
    gen = list(gen)  # in case generator is consumed
    setupfuncs = list(setupfuncs)
    sigs = []
    if mapfunc is not None:
        if not setupfuncs:
            setupfuncs.append(None)
        for setupfunc in setupfuncs:
            sigs.append((mapfunc, setupfunc))
    else:
        for mapfunc in setupfuncs:
            sigs.append((mapfunc, None))
    for mapfunc, setupfunc in sigs:
        time = maptime(gen, mapfunc, setupfunc)
        sig = _map_setup_call_sig(mapfunc, setupfunc) % 'x'
        plt.plot(gen, time, label=sig)
        plt.legend(loc='upper left')
        print("benched %s" % sig)
    plt.xlabel('x')


if __name__ == '__main__':
    # Tree with all non-root nodes connected directly to root
    def flattree(n): return rangefunc([0]*n)

    # Endofunction with f[0] == 0 and f[n] == n-1 for n in f.domain
    def talltree(n): return rangefunc([0] + list(range(n)))

    # Cyclic permutation of range(n)
    def bigcycle(n): return rangeperm(list(range(1, n)) + [0])

    def balanced_binary_tree(n):
        """Produce a balanced binary tree of height n."""
        h = int(log2(n))
        tree = [h]
        while h:
            h -= 1
            tree *= 2
            tree = [h] + tree
        return rangefunc(LevelSequence(tree).map_labelling())

    def scattered_tree(n):
        """Tree with a big cycle and things attached"""
        return Endofunction(list(bigcycle(n//2))+list(talltree(n-n//2)))

    iteration_time(fixed_lex_partitions(100, 40))
    iteration_time(EndofunctionStructures(12))
    iteration_time(EndofunctionStructures, 12)
    iteration_time(productrange, -2, [2, 2, 2, 3, 5], step=2)

    mapbench(range(1, 2000), Endofunction.cycles, flattree)
    mapbench(range(20, 2000), Endofunction.cycles, randfunc)
    mapbench(range(20, 2000), periodicity,
             lambda f: list(randfunc(f).values()))
    plt.figure()
    mapbench(
        range(20, 2500), Endofunction.cycles,
        randfunc,
        identity,
        randperm,
        talltree,
        balanced_binary_tree,
        bigcycle,
        scattered_tree
    )
    plt.show()
