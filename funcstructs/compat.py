"""Compatibility module for CPython and PyPy 2 and 3, and Jython.

Collected by Caleb Levy from 2014-2015, mostly from other places.
"""

import platform

try:
    from itertools import accumulate  # use C speed iterator if > py3.2
except ImportError:
    import operator

    # Taken from python.org
    def accumulate(iterable, func=operator.add):
        'Return running totals'
        # accumulate([1,2,3,4,5]) --> 1 3 6 10 15
        # accumulate([1,2,3,4,5], operator.mul) --> 1 2 6 24 120
        it = iter(iterable)
        total = next(it)
        yield total
        for element in it:
            total = func(total, element)
            yield total

try:  # prefer maintained version when available
    from six import with_metaclass, viewitems
except ImportError:
    def with_metaclass(meta, *bases):
        """Create a base class with a metaclass."""
        # This requires a bit of explanation: the basic idea is to make a dummy
        # metaclass for one level of class instantiation that replaces itself
        # with the actual metaclass.
        class metaclass(meta):
            def __new__(cls, name, this_bases, d):
                return meta(name, bases, d)
        return type.__new__(metaclass, 'temporary_class', (), {})

    viewitems = getattr(dict, "viewitems", dict.items)


PLATFORM = platform.python_implementation()  # Save an import in a few places


def Jython_Function_eq(self, other):
    # Hack to make Function work in Jython, where overriding dict.__getitem__
    # breaks the default __eq__. The explicit conversion to dict needlessly
    # and measurably slows down other implementations (unlike
    # frozendict.__hash__, which makes no measurable differene), so we
    # conditionally add it for Jython's sake.
    if type(self) is type(other):
        return dict(self) == dict(other)
    return False
# Mask custom name; this implementation detail should be transparent to users.
Jython_Function_eq.__name__ = '__eq__'
