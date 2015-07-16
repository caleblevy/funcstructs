"""Immutable multiset data structure.

Caleb Levy, 2015.
"""


from collections import Counter, Mapping

from frozendict import frozendict, _map_get, _map_set


# Internally store Counter instead of dict, both for speed and for easier
# interaction with addition methods in python2.
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
        mset = Counter()
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
                    dict.__setitem__(mset, el, mset.get(el, 0) + 1)
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


_MultisetHelper(Multiset)


print(Multiset([1, 1, 2, 2, 3]))
print(Multiset({'a': 1}))
print(Multiset(a=1))
print(Multiset("abracadabra"))
# print(Multiset({}, b=2))
# print(Multiset({'a': 'b'}))
print(Multiset.__new__(frozendict))
print(Counter.__new__(dict))
