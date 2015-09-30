"""Compatibility module for CPython and PyPy 2 and 3, and Jython.

Collected by Caleb Levy from 2014-2015, mostly from other places.
"""

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


# Copied directly from the six compatibility module
def with_metaclass(meta, *bases):
    """Create a base class with a metaclass."""
    # This requires a bit of explanation: the basic idea is to make a dummy
    # metaclass for one level of class instantiation that replaces itself
    # with the actual metaclass.
    class metaclass(meta):
        def __new__(cls, name, this_bases, d):
            return meta(name, bases, d)
    return type.__new__(metaclass, 'temporary_class', (), {})


def is_index(x):
    """Return whether the object x can be used as an index."""
    # Can't use isinstance(x, numbers.Integral) since sympy.Integer and
    # sage.Integer are not registered under that ABC.
    #
    # Can't check hasattr(x, '__index__') since sage uses some insane
    # metaclass/dynamic attribute weirdness weirdness and this test fails on
    # its integers.
    #
    # Also tried testing the result of range(x) for an error; this fails since
    # sympy and sage floats that are integer valued seem to work here for
    # whatever reason.
    #
    # Can't check tuple()[x] for an IndexError (as opposed to TypeError) since
    # slices would pass silently. We could combine tests 2 and 3, but this is
    # way easier.
    return hasattr(type(x), '__index__')


def is_natural(x):
    """Return whether the object x is a positive integer."""
    return is_index(x) and x > 0
