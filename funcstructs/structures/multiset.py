"""Immutable multiset data structure.

Caleb Levy, 2015.
"""

from __future__ import print_function

from collections import Counter, Mapping
from functools import reduce
from itertools import chain, combinations_with_replacement, product
from math import factorial
from operator import mul

from funcstructs.bases.frozendict import frozendict, _map_get, _map_set

__all__ = ["Multiset", "unordered_product", "counts", "sorted_counts"]


def _binop_template(name, map_get, map_set):
    """Template for wrapping binary operations from Counter to Multiset"""
    counter_op = getattr(Counter, name)

    def binop(self, other):
        if isinstance(other, Multiset):
            other = map_get(other)
        result = object.__new__(Multiset)
        map_set(result, counter_op(map_get(self), other))
        return result
    binop.__name__ = name
    binop.__doc__ = counter_op.__doc__.replace("Counter", "Multiset").replace(
        "counter", "multiset")
    return binop


def _rop_template(name, map_get, map_set):
    """Make reversed binary ops for Multiset using Counter methods."""
    binop = getattr(Counter, '__'+name[3:])

    def rop(self, other):
        return binop(other, map_get(self))
    rop.__name__ = name
    rop.__doc__ = None
    return rop


def _MultisetHelper(ms_cls, map_get=_map_get, map_set=_map_set):
    """Add Counter wrappers to Multiset."""

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
        # Not calling Counter directly skips __init__, which speeds up tests by
        # about 5 %, since we construct hundreds of thousands of Multisets.
        mset = dict.__new__(Counter)
        check = False
        if len(args) == 2:
            if kwargs:
                raise TypeError("Multiset does not accept iterable and kwargs")
            iterable = args[1]
            if isinstance(iterable, Mapping):
                dict.update(mset, iterable)
                check = True
            else:
                for el in iterable:
                    # mset is a Counter, so if item is missing then mset[el]
                    # returns 0, to which we add 1.
                    mset[el] += 1
        elif kwargs:
            dict.update(mset, kwargs)
            check = True
        elif len(args) > 2:
            raise TypeError("expected at most 2 arguments, got %d" % len(args))
        if check:
            if not all((isinstance(v, int) and v > 0) for v in mset.values()):
                raise TypeError("multiplicities must be positive integers")
        map_set(self, mset)
        return self

    ms_cls.__new__ = staticmethod(__new__)

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


def unordered_product(mset, iterfunc):
    """Given a multiset of inputs to an iterable, and iterfunc, returns all
    unordered combinations of elements from iterfunc applied to each el. It is
    equivalent to:

        set(Multiset(p) for p in product([iterfunc(i) for i in mset]))

    except it runs through each element once. This program makes the
    assumptions that no two members of iterfunc(el) are the same, and that if
    el1 != el2 then iterfunc(el1) and iterfunc(el2) are mutually disjoint."""
    mset = Multiset(mset)
    strands = []
    for y, d in mset.items():
        strands.append(combinations_with_replacement(iterfunc(y), d))
    for bundle in product(*strands):
        yield Multiset(chain(*bundle))


def counts(elements):
    """Split an iterable (or mapping) into corresponding key-value lists."""
    mset = Multiset(elements)
    return tuple(mset.keys()), tuple(mset.values())


def sorted_counts(elements):
    """Same as counts with both lists sorted first by key then by count."""
    items = Multiset(elements).items()
    if items:
        return tuple(zip(*sorted(items)))
    else:
        return (), ()


if __name__ == '__main__':
    print(Multiset([1, 1, 2, 2, 3]))
    print(Multiset({'a': 1}))
    print(Multiset(a=1))
    print(Multiset("abracadabra"))
    # print(Multiset({}, b=2))
    # print(Multiset({'a': 'b'}))
    print(Multiset.__new__(frozendict))
    print(Counter.__new__(dict))
    print(dict(Multiset("abracadabra")) == Multiset("abracadabra"))
    print(Multiset("abracadabra") == dict(Multiset("abracadabra")))
    abra = Multiset("abracadabra")
    print(list(abra))
    print(len(abra))
    print(abra.num_unique_elements())
    print(len(abra.viewitems()))

    a = Multiset("abracadabra")
    b = Multiset(range(3))
    c = Counter(a)
    d = Counter(b)

    # print(a, b, c, d)
    print(a + b)
    print(a + c)
    print(a - c)
    print(c - a)
    print(repr(c + a))
    print(type(c + a))
    print(a.degeneracy())
    print(a.values())
    print(Multiset().degeneracy())
