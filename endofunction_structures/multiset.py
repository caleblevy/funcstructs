# Copyright (C) 2014-2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.

""" Data structure for representing a multiset - also known as a bag, or
unordered tuple. """

from collections import Counter
import operator

from sympy.utilities.iterables import multiset_partitions
from memoized_property import memoized_property

from . import counts


class Multiset(Counter):
    """ Multiset is represented as a dictionary (hash table) whose keys are the
    elements of the set and values are the multiplicities. Multiset is
    immutable, and thus suitable for use as a dictionary key. """

    def __new__(cls, iterable=None):
        if isinstance(iterable, cls):
            return iterable
        self = dict.__new__(cls)
        if iterable is not None:
            for el in iterable:
                dict.__setitem__(self, el, self.get(el, 0) + 1)
        return self

    def __init__(self, iterable=None):
        pass  # Override Counter.__init__ to avoid call to self.update()

    # Disable all inherited mutating methods. Based on answers from
    #    http://stackoverflow.com/questions/1151658/python-hashable-dicts

    def __setitem__(self, key, value):
        raise TypeError("{0} is immutable and does not support item assignment"
                        .format(self.__class__.__name__))

    def __delitem__(self, key):
        raise TypeError("{0} is immutable and does not support item removal"
                        .format(self.__class__.__name__))

    def clear(self):
        raise TypeError("{0} is immutable and does not support item removal"
                        .format(self.__class__.__name__))

    def pop(self, *args, **kwargs):
        raise TypeError("{0} is immutable and does not support item removal"
                        .format(self.__class__.__name__))

    def popitem(self, *args, **kwargs):
        raise TypeError("{0} is immutable and does not support item removal"
                        .format(self.__class__.__name__))

    def setdefault(self, *args, **kwargs):
        raise TypeError("{0} is immutable and does not support item assignment"
                        .format(self.__class__.__name__))

    def update(self, *args, **kwargs):
        raise TypeError("{0} is immutable and does not support item assignment"
                        .format(self.__class__.__name__))

    # Override Counter len; length of a multiset is total number of elements.

    def __len__(self):
        return sum(self.values())

    @memoized_property
    def _hash(self):
        return hash(frozenset(self.items()))

    def __hash__(self):
        return self._hash

    def __repr__(self):
        """ The string representation is a call to the constructor given a
        tuple containing all of the elements. """
        if len(self) == 0:
            return '{0}()'.format(self.__class__.__name__)
        format_str = '{cls}({tup!r})'
        return format_str.format(cls=self.__class__.__name__, tup=tuple(self))

    def __str__(self):
        """The printable string appears just like a set, except that each
        element is raised to the power of the multiplicity if it is greater
        than 1. """
        if len(self) == 0:
            return '{class_name}()'.format(class_name=self.__class__.__name__)
        else:
            format_single = '{elem!r}'
            format_mult = '{elem!r}^{mult}'
            strings = []
            for elem, mult in self.items():
                # Hack to make nested multisets print in bracket form.
                if isinstance(elem, self.__class__):
                    mstring = str(elem)
                    if mult > 1:
                        mstring += '^%s' % mult
                    strings.append(mstring)
                    continue
                if mult > 1:
                    strings.append(format_mult.format(elem=elem, mult=mult))
                else:
                    strings.append(format_single.format(elem=elem))
            return '{%s}' % ', '.join(strings)

    def unique_elements(self):
        return self.keys()

    def __iter__(self):
        """Iterate through all elements; return multiple copies if present."""
        return self.elements()

    def split(self):
        """ Splits the multiset into element-multiplicity pairs. """
        y = list(self.keys())
        d = [self[el] for el in y]
        return y, d

    def sort_split(self):
        y = []
        d = []
        for elem, mult in sorted(self.items(), key=operator.itemgetter(0)):
            y.append(elem)
            d.append(mult)
        return y, d

    def degeneracy(self):
        """ Number of different representations of the same multiset. """
        return counts.factorial_prod(self.values())

    def partitions(self):
        """ Yield partitions of a multiset, each one being a multiset of
        multisets. """
        for mpart in multiset_partitions(list(self)):
            yield self.__class__(self.__class__(m) for m in mpart)
