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


import heapq
import collections
from functools import reduce
from math import factorial
from operator import mul, itemgetter

from memoized_property import memoized_property
from sympy.utilities.iterables import multiset_partitions


prod = lambda iterable: reduce(mul, iterable, 1)
factorial_prod = lambda iterable: prod(factorial(I) for I in iterable)
nCk = lambda n, k: factorial(n)//factorial(k)//factorial(n-k)


class Multiset(collections.Counter):
    """ Multiset - Also known as a Multiset or unordered tuple. Multiset is
    Hashable, thus it is immutable and usable for dict keys. """

    def __init__(self, iterable=None):
        self._size = 0
        self._items = frozenset()
        self._hash = hash(self._items)
        super(dict, self).__init__()
        if iterable is not None:
            if isinstance(iterable, self.__class__):
                super(collections.Counter, self).update(iterable)
                self._size = iterable._size
                self._hash = iterable._hash
                self._items = iterable._items
            else:
                for el in iterable:
                    super(collections.Counter, self).__setitem__(el, self.get(el, 0)+1)
                    self._size += 1
                self._items = frozenset(self.items())
                self._hash = hash(self._items)

    def __setitem__(self, key, value):
        raise TypeError("{0} does not support item assignment"
                         .format(self.__class__.__name__))
    def __delitem__(self, key):
        raise TypeError("{0} does not support item assignment"
                         .format(self.__class__.__name__))
    def clear(self):
        raise TypeError("{0} does not support item assignment"
                         .format(self.__class__.__name__))
    def pop(self, *args, **kwargs):
        raise TypeError("{0} does not support item assignment"
                         .format(self.__class__.__name__))
    def popitem(self, *args, **kwargs):
        raise TypeError("{0} does not support item assignment"
                         .format(self.__class__.__name__))
    def setdefault(self, *args, **kwargs):
        raise TypeError("{0} does not support item assignment"
                         .format(self.__class__.__name__))
    def update(self, *args, **kwargs):
        raise TypeError("{0} does not support item assignment"
                         .format(self.__class__.__name__))

    def __len__(self):
        return self._size

    def __hash__(self):
        return self._hash

    def __repr__(self):
        """The string representation is a call to the constructor given a tuple
        containing all of the elements. This runs in whatever tuple(self) does,
        I'm assuming O(len(self)). """
        if self._size == 0:
            return '{0}()'.format(self.__class__.__name__)

        format_str = '{cls}({tup!r})'
        return format_str.format(cls=self.__class__.__name__, tup=tuple(self))

    def __str__(self):
        """The printable string appears just like a set, except that each
        element is raised to the power of the multiplicity if it is greater
        than 1. This runs in O(self.num_elements()). """
        if self._size == 0:
            return '{class_name}()'.format(class_name=self.__class__.__name__)
        else:
            format_single = '{elem!r}'
            format_mult = '{elem!r}^{mult}'
            strings = []
            for elem, mult in self.items():
                # Hack to make multisets print with parentheses.
                if isinstance(elem, self.__class__):
                    mstring = str(elem)
                    if mult > 1:
                        mstring += '^%s'%str(mult)
                    strings.append(mstring)
                    continue
                if mult > 1:
                    strings.append(format_mult.format(elem=elem, mult=mult))
                else:
                    strings.append(format_single.format(elem=elem))
            return '{%s}' % ', '.join(strings)

    ## New public methods (not overriding/implementing anything)
    @memoized_property
    def num_elements(self):
        """ Returns the number of unique elements. This runs in O(1) time. """
        return len(self.values())

    def count(self, value):
        """Return the number of value present in this Multiset. If value is not
        in the Multiset no Error is raised, instead 0 is returned. This runs in
        O(1) time.

        Args:
            value: The element of self to get the count of
        Returns:
            int: The count of value in self
        """
        return self.get(value, 0)

    def __contains__(self, value):
        """ Returns the multiplicity of the element. This runs in O(1). """
        return self.count(value)

    def __iter__(self):
        """Iterate through all elements; return multiple copies if present."""
        for elem, count in self.items():
            for i in range(count):
                yield(elem)

    # Comparison methods

    def __le__(self, other):
        """ Tests if self <= other where other is another multiset This runs in
        O(l + n) where:

            n is self.num_elements()
            if other is a multiset:
                l = 1
            else:
                l = len(other)
        """
        if not isinstance(other, self.__class__):
            raise TypeError("Cannot compare Multiset with another type.")
        if len(self) > len(other):
            return False
        for elem in self.elements():
            if self.count(elem) > other.count(elem):
                return False
        return True

    def __lt__(self, other):
        return self <= other and len(self) < len(other)

    def __gt__(self, other):
        return other < self

    def __ge__(self, other):
        return other <= self

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._items == other._items
        return False

    def __ne__(self, other):
        return not (self == other)

    def split(self):
        """ Splits the multiset into element-multiplicity pairs. """
        y = list(self.keys())
        d = [self[el] for el in y]
        return y, d

    def sort_split(self):
        y = []
        d = []
        for elem, mult in sorted(self.items(), key=itemgetter(0)):
            y.append(elem)
            d.append(mult)
        return y, d

    def degeneracy(self):
        """ Number of different representations of the same multiset. """
        y, d = self.split()
        return factorial_prod(d)

    def partitions(self):
        """ Yield partitions of a multiset, each one being a multiset of
        multisets. """
        for mpart in multiset_partitions(list(self)):
            yield self.__class__(self.__class__(m) for m in mpart)
