"""Data structure for representing a multiset - also known as a bag, or
unordered tuple.

Caleb Levy, 2014 and 2015.
"""

from itertools import chain, combinations_with_replacement, product
from collections import Counter

from funcstructs.bases import frozendict
from funcstructs.utils.combinat import factorial_prod

__all__ = ["Multiset", "unordered_product"]


def _get_method_with_docs(methodname):
    """Return a method function from Counter with 'Counter' replaced by
    'Multiset' in the docstring."""
    method = Counter.__dict__[methodname]
    doc = method.__doc__
    doc = doc.replace("Counter({", "Multiset._frommap({")  # dict input
    doc = doc.replace("Counter", "Multiset").replace("counter", "multiset")
    method.__doc__ = doc
    return method


def _binop_template(name):
    """Template for copying binary operations from Counter to Multiset"""
    counterop = _get_method_with_docs(name)  # localize for speed

    def binop(self, other):
        if isinstance(other, Multiset):
            other = Counter(other)
        return Multiset._frommap(counterop(Counter(self), other))
    binop.__name__ = name
    binop.__doc__ = counterop.__doc__
    return binop


def _rop_template(name):
    """Template for reversed binary operations"""
    def binop(self, other):
        return getattr(other, '__'+name[3:])(Counter(self))
    binop.__name__ = name
    binop.__doc__ = None
    return binop


class Multiset(frozendict):
    """ Multiset is represented as a dictionary (hash table) whose keys are the
    elements of the set and values are the multiplicities. Multiset is
    immutable, and thus suitable for use as a dictionary key. """

    __slots__ = ()

    def __new__(cls, iterable=None):
        self = dict.__new__(cls)
        if iterable is not None:
            for el in iterable:
                dict.__setitem__(self, el, self.get(el, 0) + 1)
        return self

    @classmethod
    def _frommap(cls, *args, **kwargs):
        """Multiset from any objects usable to make dictionaries."""
        mset = cls()
        for k, v in dict(*args, **kwargs).items():
            if not(isinstance(v, int) and v > 0):
                raise TypeError("%s keys must be positive integers" % cls)
            dict.__setitem__(mset, k, v)
        return mset

    # length of a multiset includes multiplicities
    def __len__(self):
        return sum(self.values())

    # Iterate through all elements; return multiple copies if present.
    __iter__ = Counter.__dict__['elements']

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

    most_common = _get_method_with_docs("most_common")

    (__add__, __sub__, __and__, __or__) = map(
        _binop_template, ['__add__', '__sub__', '__and__', '__or__'])

    (__radd__, __rsub__, __rand__, __ror__) = map(
        _rop_template, ['__radd__', '__rsub__', '__rand__', '__ror__'])

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
        strands.append(combinations_with_replacement(iterfunc(y), d))
    for bundle in product(*strands):
        yield Multiset(chain(*bundle))
