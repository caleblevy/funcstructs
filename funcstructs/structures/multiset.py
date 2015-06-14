"""Data structure for representing a multiset - also known as a bag, or
unordered tuple.

Caleb Levy, 2014 and 2015.
"""

from itertools import chain, combinations_with_replacement, product
from collections import Counter, Mapping

from funcstructs.bases import frozendict
from funcstructs.utils.combinat import factorial_prod

__all__ = ["Multiset", "unordered_product"]


def _replace_doc(method):
    if isinstance(method, str):
        method = getattr(Counter, method)
    doc = method.__doc__
    return doc.replace("Counter", "Multiset").replace("counter", "multiset")


def _get_method_with_docs(methodname):
    """Return a method function from Counter with 'Counter' replaced by
    'Multiset' in the docstring."""
    method = Counter.__dict__[methodname]
    method.__doc__ = _replace_doc(method)
    return method


def _binop_template(name):
    """Template for copying binary operations from Counter to Multiset"""
    counterop = _get_method_with_docs(name)  # localize for speed

    def binop(self, other):
        if isinstance(other, Multiset):
            other = Counter(other)
        return Multiset(counterop(Counter(self), other))
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


def _check_multiset(mset):
    """Return True if all elements of a mapping are positive integers."""
    if all((isinstance(v, int) and v > 0) for v in mset.values()):
        return True
    raise TypeError("multiplicities must be positive integers")


class Multiset(frozendict):
    """ Multiset is represented as a dictionary (hash table) whose keys are the
    elements of the set and values are the multiplicities. Multiset is
    immutable, and thus suitable for use as a dictionary key. """

    __slots__ = ()

    def __new__(*args, **kwargs):
        self = dict.__new__(*args, **kwargs)
        if len(args) == 2:
            if kwargs:
                raise TypeError("Multiset does not accept iterable and kwargs")
            iterable = args[1]
            if isinstance(iterable, Mapping):
                dict.update(self, iterable)
                _check_multiset(self)
            else:
                for el in iterable:
                    dict.__setitem__(self, el, self.get(el, 0) + 1)
        elif kwargs:
            dict.update(self, kwargs)
            _check_multiset(self)
        elif len(args) > 2:
            raise TypeError("expected at most 2 arguments, got %d" % len(args))
        return self
    __new__.__doc__ = _replace_doc("__init__")

    def __len__(self):
        """Length of a multiset, including multiplicities."""
        return sum(self.values())

    elements = _get_method_with_docs("elements")

    def __iter__(self):
        """Iterate through the underlying set, returning multiple copies of the
        elements if present. Equivalent to Counter.elements()."""
        return self.elements()

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
