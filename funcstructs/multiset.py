"""Data structure for representing a multiset - also known as a bag, or
unordered tuple.

Caleb Levy, 2014 and 2015.
"""

import collections
import functools
import math
import operator

__all__ = ["Multiset"]


# functions publicly accessed through combinat are defined here so that
# structures.core is self-contained.
def _prod(iterable):
    """Product of all items in an iterable."""
    return functools.reduce(operator.mul, iterable, 1)


def _factorial_prod(iterable):
    """Product of factorial of elements in an iterable."""
    return _prod(math.factorial(i) for i in iterable)


@classmethod
def _raise_unassignable(cls, *args, **kwargs):
    raise TypeError('%r does not support item assignment' % cls.__name__)


@classmethod
def _raise_undeleteable(cls, *args, **kwargs):
    raise TypeError('%r does not support item deletion' % cls.__name__)


class Multiset(dict):
    """ Multiset is represented as a dictionary (hash table) whose keys are the
    elements of the set and values are the multiplicities. Multiset is
    immutable, and thus suitable for use as a dictionary key. """

    __slots__ = ()

    def __new__(cls, iterable=None):
        if isinstance(iterable, cls):
            return iterable
        self = dict.__new__(cls)
        if iterable is not None:
            for el in iterable:
                dict.__setitem__(self, el, self.get(el, 0) + 1)
        return self

    def __init__(self, *args, **kwargs):
        pass  # Override dict.__init__ to avoid call to self.update()

    # Disable all inherited mutating methods. Based on brownie's ImmutableDict

    __setitem__ = setdefault = update = _raise_unassignable

    __delitem__ = clear = pop = popitem = _raise_undeleteable

    # length of a multiset includes multiplicities
    def __len__(self):
        return sum(self.values())

    # Iterate through all elements; return multiple copies if present.
    __iter__ = collections.Counter.__dict__['elements']

    def __hash__(self):
        return hash(frozenset(self.items()))

    def __repr__(self):
        """ The string representation is a call to the constructor given a
        tuple containing all of the elements. """
        return "%s(%s)" % (self.__class__.__name__, list(self))

    def __str__(self):
        """The printable string appears just like a set, except that each
        element is raised to the power of the multiplicity if it is greater
        than 1. """
        contents = []
        for el, mult in self.items():
            if isinstance(el, self.__class__):
                el_str = str(el)
            else:
                el_str = repr(el)
            if mult > 1:
                el_str += '^%s' % mult
            contents.append(el_str)
        return '{%s}' % ', '.join(contents)

    def split(self):
        """Splits the multiset into element-multiplicity pairs."""
        y = list(self.keys())
        d = [self[el] for el in y]
        return y, d

    most_common = collections.Counter.__dict__['most_common']

    def sort_split(self):
        """Same as Multiset.split with both lists sorted by elements"""
        y = []
        d = []
        for elem, mult in sorted(self.items(), key=operator.itemgetter(0)):
            y.append(elem)
            d.append(mult)
        return y, d

    def degeneracy(self):
        """Number of different representations of the same multiset."""
        return _factorial_prod(self.values())
