"""Immutable multiset data structure.

Caleb Levy, 2014 and 2015.
"""

from itertools import chain, combinations_with_replacement, product
from collections import Counter, Mapping

from funcstructs.bases import frozendict
from funcstructs.utils.combinat import factorial_prod

__all__ = ["Multiset", "unordered_product", "counts", "sorted_counts"]


class Multiset(frozendict):
    """Dict subclass for counting hashable items.  Sometimes called a bag
    or multiset.  Elements are stored as dictionary keys and their counts
    are stored as dictionary values.

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

    def __new__(*args, **kwargs):  # signature allows using `cls` keyword arg
        """Create a new Multiset. If given, count elements from an
        input iterable, otherwise initialize the count from another
        mapping of elements to their multiplicities.

        >>> m = Multiset()                      # a new, empty Multiset
        >>> m = Multiset('gallahad')            # Multiset from an iterable
        >>> m = Multiset({'a': 4, 'b': 2})      # Multiset from a mapping
        >>> m = Multiset(a=4, b=2)              # Multiset from keyword args
        """
        self = frozendict.__new__(args[0])
        check = False
        if len(args) == 2:
            if kwargs:
                raise TypeError("Multiset does not accept iterable and kwargs")
            iterable = args[1]
            if isinstance(iterable, Mapping):
                dict.update(self, iterable)
                check = True
            else:
                for el in iterable:
                    dict.__setitem__(self, el, self.get(el, 0) + 1)
        elif kwargs:
            dict.update(self, kwargs)
            check = True
        elif len(args) > 2:
            raise TypeError("expected at most 2 arguments, got %d" % len(args))
        if check:
            if not all((isinstance(v, int) and v > 0) for v in self.values()):
                raise TypeError("multiplicities must be positive integers")
        return self

    @classmethod
    def fromkeys(cls, iterable, v=None):
        raise NotImplementedError("%s.fromkeys() is undefined." % cls.__name__)

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
        return dict.__len__(self)  # cannot use len(dict.viewkeys()) in pypy

    most_common = Counter.__dict__['most_common']
    most_common.__doc__ = most_common.__doc__.replace("Counter", "Multiset")

    def degeneracy(self):
        """Number of different representations of the same multiset."""
        return factorial_prod(self.values())

    __repr__ = Counter.__dict__['__repr__']


# Save some effort and copy the binary operations directly from Counter
_binops = ['__add__', '__sub__', '__and__', '__or__']


def _binop_maker(name):
    """Template for copying binary operations from Counter to Multiset"""
    counterop = Counter.__dict__[name]

    def binop(self, other):
        if isinstance(other, Multiset):
            other = Counter(other)
        return Multiset(counterop(Counter(self), other))
    binop.__name__ = name
    binop.__doc__ = counterop.__doc__.replace("Counter", "Multiset").replace(
        "counter", "multiset")
    return binop


for binop in _binops:
    setattr(Multiset, binop, _binop_maker(binop))


# Make sure Counter + Multiset returns a Counter
_rops = ['__radd__', '__rsub__', '__rand__', '__ror__']


def _rop_maker(name):
    """Make reversed binary ops for Multiset using Counter methods."""
    def rop(self, other):
        # convert self to a Counter, and retry other.__op__(self).
        return getattr(other, '__'+name[3:])(Counter(self))
    rop.__name__ = name
    rop.__doc__ = None
    return rop


for rop in _rops:
    setattr(Multiset, rop, _rop_maker(rop))


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
