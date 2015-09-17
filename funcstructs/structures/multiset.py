"""Immutable multiset data structure.

Caleb Levy, 2015.
"""

from __future__ import print_function

from heapq import nlargest
from collections import Counter, Mapping
from functools import reduce
from itertools import chain, starmap, repeat
from math import factorial
from operator import itemgetter, mul

from funcstructs.bases.frozendict import frozendict, _map_accessors

__all__ = ["Multiset"]


def _prod(iterable):
    """Product of all items in an iterable."""
    return reduce(mul, iterable, 1)


def _factorial_prod(iterable):
    """Product of factorial of elements in an iterable."""
    return _prod(map(factorial, iterable))


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


def _MultisetHelper(ms_cls):
    """Add Counter wrappers to Multiset."""

    map_set, map_get = _map_accessors()

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
        # Store dict instead of Counter internally for speed.
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
                    mset[el] = mset.get(el, 0) + 1
        elif kwargs:
            mset.update(kwargs)  # will need in py3.6 with **kwargs OrderedDict
            check = True
        elif len(args) > 2:
            raise TypeError("expected at most 1 argument, got %d" % len(args))
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

    global _MultisetHelper
    del _MultisetHelper

    return ms_cls


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

    >>> ''.join(sorted(m.elements()))    # list unique elements
    'abcdr'

    >>> m['a']                           # count of letter 'a'
    5
    """

    __slots__ = ()

    @classmethod
    def fromkeys(cls, iterable, v=None):
        raise NotImplementedError("%s.fromkeys() is undefined." % cls.__name__)

    @classmethod
    def fromitems(cls, items):
        """Return a Multiset from an iterable of element-multiplicity
        pairs."""
        return cls(dict(items))

    def __repr__(self):
        try:
            items = sorted(self._items())
        except TypeError:
            # handle case where elements are not orderable
            items = self.most_common()
        item_string = ', '.join(map('%r: %r'.__mod__, items))
        return '%s({%s})' % (self.__class__.__name__, item_string)

    def __len__(self):
        """Length of a multiset, including multiplicities."""
        return sum(self._values())

    def __iter__(self):
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
        return chain.from_iterable(starmap(repeat, self._items()))

    def elements(self):
        """Underlying set of unique elements.

        >>> m = Multiset("abracadabra")
        >>> sorted(m.elements())
        ['a', 'b', 'c', 'd', 'r']
        """
        return self._keys()

    def num_unique_elements(self):
        """Number of unique elements in the Multiset.

        >>> Multiset("abracadabra").num_unique_elements()
        5
        """
        return len(self.elements())

    def most_common(self, n=None):
        """List the n most common elements and their counts from the most
        common to the least.  If n is None, then list all element counts.

        >>> Multiset('abcdeabcdabcaba').most_common(3)
        [('a', 5), ('b', 4), ('c', 3)]
        """
        # Emulate Bag.sortedByCount from Smalltalk
        if n is None:
            return sorted(self._items(), key=itemgetter(1), reverse=True)
        return nlargest(n, self._items(), key=itemgetter(1))

    def degeneracy(self):
        """Number of different representations of the same multiset."""
        return _factorial_prod(self._values())
