"""Data structure for representing a multiset - also known as a bag, or
unordered tuple.

Caleb Levy, 2014 and 2015.
"""

import collections
import itertools
import operator

from .combinat import factorial_prod

__all__ = ["Multiset"]


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
        return factorial_prod(self.values())


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
        strands.append(itertools.combinations_with_replacement(iterfunc(y), d))
    for bundle in itertools.product(*strands):
        yield Multiset(itertools.chain.from_iterable(bundle))
