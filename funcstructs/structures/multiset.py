"""Immutable multiset data structure.

Caleb Levy, 2015.
"""

from __future__ import print_function

from collections import Counter, Mapping
from functools import reduce
from math import factorial
from operator import mul

from funcstructs.bases.frozendict import frozendict, _map_get, _map_set

__all__ = ["Multiset", "counts", "sorted_counts"]


def _binop_template(name, map_get, map_set):
    """Template for wrapping binary operations from Counter to Multiset"""
    counter_op = getattr(Counter, name)

    def binop(self, other):
        if isinstance(other, Multiset):
            other = Counter(map_get(other))
        result = object.__new__(Multiset)
        map_set(result, dict(counter_op(Counter(map_get(self)), other)))
        return result
    binop.__name__ = name
    binop.__doc__ = counter_op.__doc__.replace("Counter", "Multiset").replace(
        "counter", "multiset")
    return binop


def _rop_template(name, map_get, map_set):
    """Make reversed binary ops for Multiset using Counter methods."""
    binop = getattr(Counter, '__'+name[3:])

    def rop(self, other):
        return binop(other, Counter(map_get(self)))
    rop.__name__ = name
    rop.__doc__ = None
    return rop


def _MultisetHelper(ms_cls, map_get=_map_get, map_set=_map_set):
    """Add Counter wrappers to Multiset."""

    @staticmethod
    def __new__(*args, **kwargs):  # signature allows using `cls` keyword arg
        """Create a new Multiset. If given, count elements from an
        input iterable, otherwise initialize the count from another
        mapping of elements to their multiplicities.

        >>> m = Multiset()                      # a new, empty Multiset
        >>> m = Multiset('gallahad')            # Multiset from an iterable
        >>> m = Multiset({'a': 4, 'b': 2})      # Multiset from a mapping
        >>> m = Multiset(a=4, b=2)              # Multiset from keyword args
        """
        self = object.__new__(args[0])
        mset = {}
        check = False
        if len(args) == 2:
            if kwargs:
                raise TypeError("Multiset does not accept iterable and kwargs")
            iterable = args[1]
            if isinstance(iterable, Mapping):
                mset.update(iterable)
                check = True
            else:
                for el in iterable:
                    # Use syntactic sugar for special methods, since these
                    # short-circuit to the type directly. Call directly on type
                    # for regular methods.
                    mset[el] = mset.get(el, 0) + 1
        elif kwargs:
            mset.update(kwargs)  # will need in py3.6 with **kwargs OrderedDict
            check = True
        elif len(args) > 2:
            raise TypeError("expected at most 2 arguments, got %d" % len(args))
        if check:
            if not all((isinstance(v, int) and v > 0) for v in mset.values()):
                raise TypeError("multiplicities must be positive integers")
        map_set(self, mset)
        return self
    ms_cls.__new__ = __new__

    for op in ['__add__', '__sub__', '__and__', '__or__']:
        setattr(ms_cls, op, _binop_template(op, map_get, map_set))

    for rop in ['__radd__', '__rsub__', '__rand__', '__ror__']:
        setattr(ms_cls, rop, _rop_template(rop, map_get, map_set))

    return ms_cls


# Internally store Counter instead of dict, both for speed and for easier
# interaction with addition methods in python2.
@_MultisetHelper
class Multiset(frozendict):
    """frozendict subclass for counting hashable items.  Multiset is the
    immutable counterpart to collections.Counter.  Elements are stored as
    dictionary keys and their counts are stored as dictionary values.

    >>> m = Mulitset('abracadabra')      # Multiset of elements from a string

    >>> m.most_common(3)                 # three most common elements
    [('a', 5), ('r', 2), ('b', 2)]
    >>> ''.join(sorted(m))               # list elements with repetitions
    'aaaaabbcdrr'
    >>> len(m)                           # total of all counts
    11

    >>> ''.join(sorted(c.elements()))    # list unique elements
    'abcdr'

    >>> m['a']                           # count of letter 'a'
    5
    """

    __slots__ = ()

    @classmethod
    def fromkeys(cls, iterable, v=None):
        raise NotImplementedError("%s.fromkeys() is undefined." % cls.__name__)

    __repr__ = Counter.__dict__['__repr__']

    def __len__(self):
        """Length of a multiset, including multiplicities."""
        return sum(self.values())

    __iter__ = Counter.__dict__['elements']
    __iter__.__name__ = '__iter__'
    __iter__.__doc__ = \
        """Iterate over elements repeating each as many times as its count.

        >>> m = Mulitset('ABCABC')
        >>> sorted(m))
        ['A', 'A', 'B', 'B', 'C', 'C']

        # Knuth's example for prime factors of 1836:  2**2 * 3**3 * 17**1
        >>> prime_factors = Multiset({2: 2, 3: 3, 17: 1})
        >>> product = 1
        >>> for factor in prime_factors:                # loop over factors
        ...     product *= factor                       # and multiply them
        >>> product
        1836
        """

    def elements(self):
        """Underlying set of unique elements.

        >>> m = Multiset("abracadabra")
        >>> sorted(m.elements())
        ['a', 'b', 'c', 'd', 'r']
        """
        return frozenset(self.keys())

    def num_unique_elements(self):
        """Number of unique elements in the Multiset.

        >>> m = Multiset("abracadabra").num_unique_elements()
        5
        """
        return frozendict.__len__(self)

    most_common = Counter.__dict__['most_common']
    most_common.__doc__ = most_common.__doc__.replace("Counter", "Multiset")

    def degeneracy(self):
        """Number of different representations of the same multiset."""
        return reduce(mul, map(factorial, self.values()), 1)


def counts(elements):
    """Split an iterable (or mapping) into corresponding key-value lists."""
    if type(elements) is not Multiset:
        elements = Multiset(elements)
    # Cast to tuples, due to issues with pypy's viewitems changing order even
    # if the dict has not been altered.
    return tuple(elements.keys()), tuple(elements.values())


def sorted_counts(elements):
    """Same as counts with both lists sorted first by key then by count."""
    if type(elements) is not Multiset:
        elements = Multiset(elements)
    if elements:  # "bool({}.viewitems()) is True" in Jython, sadly...
        return tuple(zip(*sorted(elements.items())))
    else:
        return (), ()
