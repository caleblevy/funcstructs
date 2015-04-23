# Copyright (C) 2014-2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.

""" Data structure for representing a multiset - also known as a bag, or
unordered tuple. """

import collections
import operator

from . import counts


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

    def split(self):
        """ Splits the multiset into element-multiplicity pairs. """
        y = list(self.keys())
        d = [self[el] for el in y]
        return y, d

    most_common = collections.Counter.__dict__['most_common']

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
