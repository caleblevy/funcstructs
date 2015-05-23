"""Data structure for representing a multiset - also known as a bag, or
unordered tuple.

Caleb Levy, 2014 and 2015.
"""

import collections
import itertools

from funcstructs import bases
from funcstructs.utils.combinat import factorial_prod
from funcstructs.utils.misc import flatten

__all__ = ["Multiset", "unordered_product"]


class Multiset(bases.frozendict):
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

    # length of a multiset includes multiplicities
    def __len__(self):
        return sum(self.values())

    # Iterate through all elements; return multiple copies if present.
    __iter__ = collections.Counter.__dict__['elements']

    def __repr__(self):
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

    most_common = collections.Counter.__dict__['most_common']

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
        yield Multiset(flatten(bundle))
