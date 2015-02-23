#!/usr/bin/env python
# Copyright (C) 2014-2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.

""" Multisets is a utilities module for performing miscellaneous operations and
finding information about sets and multisets: breaking up multisets, getting
elements of a set, and counting ways to represent them assuming certain
properties are equivalent. """


from collections import Counter
import functools
import math
import operator

from sympy.utilities.iterables import multiset_partitions


def prod(iterable):
    return functools.reduce(operator.mul, iterable, 1)


def factorial_prod(iterable):
    return prod(math.factorial(I) for I in iterable)


def nCk(n, k):
    return math.factorial(n)//math.factorial(k)//math.factorial(n-k)


class Multiset(Counter):
    __slots__ = ['_size', '_items', '_hash']
    """ Multiset - Also known as a bag or unordered tuple. Multiset is
    hashable, immutable and usable for dict keys. """

    def __init__(self, iterable=None):
        self._size = 0
        self._items = frozenset()
        self._hash = hash(self._items)
        super(dict, self).__init__()
        if iterable is not None:
            if isinstance(iterable, self.__class__):
                super(Counter, self).update(iterable)
                self._size = iterable._size
                self._hash = iterable._hash
                self._items = iterable._items
            else:
                for el in iterable:
                    super(Counter, self).__setitem__(el, self.get(el, 0) + 1)
                    self._size += 1
                self._items = frozenset(self.items())
                self._hash = hash(self._items)

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

    def __len__(self):
        return self._size

    def __hash__(self):
        return self._hash

    def __repr__(self):
        """ The string representation is a call to the constructor given a
        tuple containing all of the elements. """
        if self._size == 0:
            return '{0}()'.format(self.__class__.__name__)
        format_str = '{cls}({tup!r})'
        return format_str.format(cls=self.__class__.__name__, tup=tuple(self))

    def __str__(self):
        """The printable string appears just like a set, except that each
        element is raised to the power of the multiplicity if it is greater
        than 1. """
        if self._size == 0:
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
                        mstring += '^%s' % str(mult)
                    strings.append(mstring)
                    continue
                if mult > 1:
                    strings.append(format_mult.format(elem=elem, mult=mult))
                else:
                    strings.append(format_single.format(elem=elem))
            return '{%s}' % ', '.join(strings)

    def unique_elements(self):
        return self.keys()

    def num_unique_elements(self):
        return len(self.values())

    def num_elements(self):
        return len(self)

    def __contains__(self, value):
        """ Returns the multiplicity of the element. This runs in O(1). """
        return self.get(value, 0)

    def __iter__(self):
        """Iterate through all elements; return multiple copies if present."""
        return self.elements()

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._items == other._items
        return False

    def __ne__(self, other):
        return not self == other

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
        return factorial_prod(self.values())

    def partitions(self):
        """ Yield partitions of a multiset, each one being a multiset of
        multisets. """
        for mpart in multiset_partitions(list(self)):
            yield self.__class__(self.__class__(m) for m in mpart)
