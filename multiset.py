#!/usr/bin/env python
# Copyright (C) 2014-2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.

"""
Multisets is a utilities module for performing miscellaneous operations and
finding information about sets and multisets: breaking up multisets, getting
elements of a set, and counting ways to represent them assuming certain
properties are equivalent.
"""

import heapq
import collections
from functools import reduce
from math import factorial
from operator import mul, itemgetter
import unittest

from sympy.utilities.iterables import multiset_partitions

prod = lambda iterable: reduce(mul, iterable, 1)
factorial_prod = lambda iterable: prod(factorial(I) for I in iterable)
nCk = lambda n, k: factorial(n)//factorial(k)//factorial(n-k)


class Multiset(collections.Set, collections.Hashable):
    """
    Multiset - Also known as a Multiset or unordered tuple. Multiset is
    Hashable, thus it is immutable and usable for dict keys.
    """

    ## Basic object methods

    """
    Base class for multiset and frozenmultiset. Is not mutable and not
    hashable, so there's no reason to use this instead of either multiset or
    frozenmultiset.
    """
    ## Basic object methods

    def __init__(self, iterable=None):
        """
        Create a new basemultiset. If iterable isn't given, is None or is empty
        then the set starts empty. If iterable is a map, then it is assumed to
        be a map from elements to the number of times they should appear in the
        multiset. Otherwise each element from iterable will be added to the
        multiset however many times it appears.

        This runs in O(len(iterable))
        """
        self._dict = dict()
        self._size = 0
        if iterable:
            if isinstance(iterable, self.__class__):
                for elem, count in iterable._dict.items():
                    self._inc(elem, count)
            else:
                for value in iterable:
                    self._inc(value)

    def __repr__(self):
        """The string representation is a call to the constructor given a tuple
        containing all of the elements.

        This runs in whatever tuple(self) does, I'm assuming O(len(self))
        """
        if self._size == 0:
            return '{0}()'.format(self.__class__.__name__)
        else:
            format = '{class_name}({tuple!r})'
            return format.format(class_name=self.__class__.__name__, tuple=tuple(self))

    def __str__(self):
        """The printable string appears just like a set, except that each
        element is raised to the power of the multiplicity if it is greater
        than 1.

        This runs in O(self.num_unique_elements())
        """
        if self._size == 0:
            return '{class_name}()'.format(class_name=self.__class__.__name__)
        else:
            format_single = '{elem!r}'
            format_mult = '{elem!r}^{mult}'
            strings = []
            for elem, mult in self._dict.items():
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

    ## Internal methods

    def _set(self, elem, value):
        """Set the multiplicity of elem to count.

        This runs in O(1) time
        """
        if value < 0:
            raise ValueError
        old_count = self.count(elem)
        if value == 0:
            if elem in self:
                del self._dict[elem]
        else:
            self._dict[elem] = value
        self._size += value - old_count

    def _inc(self, elem, count=1):
        """Increment the multiplicity of value by count.

        If count <0 then decrement.
        """
        self._set(elem, self.count(elem) + count)

    ## New public methods (not overriding/implementing anything)

    def num_unique_elements(self):
        """ Returns the number of unique elements. 
        
        This runs in O(1) time
        """
        return len(self._dict)

    def unique_elements(self):
        """ Returns a view of unique elements in this multiset. 
        
        This runs in O(1) time
        """
        return self._dict.keys()

    def count(self, value):
        """Return the number of value present in this Multiset.

        If value is not in the Multiset no Error is raised, instead 0 is returned.

        This runs in O(1) time

        Args:
            value: The element of self to get the count of
        Returns:
            int: The count of value in self
        """
        return self._dict.get(value, 0)
    
    def nlargest(self, n=None):
        """ List the n most common elements and their counts from the most
        common to the least.  If n is None, the list all element counts.

        Run time should be O(m log m) where m is len(self).
        """
        if n is None:
            return sorted(self._dict.items(), key=itemgetter(1), reverse=True)
        else:
            return heapq.nlargest(n, self._dict.items(), key=itemgetter(1))

    @classmethod
    def _from_iterable(cls, it):
        return cls(it)

    @classmethod
    def _from_map(cls, map_):
        """
        Creates a multiset from a dict of elem->count. Each key in the dict is
        added if the value is > 0.

        This runs in O(len(map))
        """
        out = cls()
        for elem, count in map_.items():
            out._inc(elem, count)
        return out

    def copy(self):
        """Create a shallow copy of self.

        This runs in O(len(self.num_unique_elements()))
        """
        return self._from_map(self._dict)
    
    ## implementing Sized methods

    def __len__(self):
        """Returns the cardinality of the Multiset.

        This runs in O(1)
        """
        return self._size

    ## implementing Container methods

    def __contains__(self, value):
        """Returns the multiplicity of the element.

        This runs in O(1)
        """
        return self.count(value)

    ## implementing Iterable methods

    def __iter__(self):
        """Iterate through all elements; return multiple copies if present."""
        for elem, count in self._dict.items():
            for i in range(count):
                yield(elem)

    # Comparison methods

    def __le__(self, other):
        """Tests if self <= other where other is another multiset

        This runs in O(l + n) where:
            n is self.num_unique_elements()
            if other is a multiset:
                l = 1
            else:
                l = len(other)
        """
        if not isinstance(other, self.__class__):
            raise TypeError("Cannot compare Multiset with another type.")
        if len(self) > len(other):
            return False
        for elem in self.unique_elements():
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
        if not isinstance(other, self.__class__):
            return False
        return len(self) == len(other) and self <= other

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return self._hash()

    # Truthiness methods
    def __bool__(self):
        return self._size

    __nonzero__ = __bool__

    def split(self):
        """Splits the multiset into element-multiplicity pairs."""
        y = list(self._dict)
        d = [self._dict[el] for el in y]
        return y, d

    def degeneracy(self):
        """Number of different representations of the same multiset."""
        y, d = self.split()
        return factorial_prod(d)

    def partitions(self):
        """
        Yield partitions of a multiset, each one being a multiset of multisets.
        """
        return multiset_partitions(list(self))


def compare_Multiset_string(b):
    s = str(b)
    return set(s.lstrip('{').rstrip('}').split(', '))


class MultisetTests(unittest.TestCase):
    """
    Test properties of Multiset objects. Tests tend to be of two forms:
        basemultiset()                     # create empty set
        basemultiset('abracadabra')        # create from an Iterable
    """

    def test_init(self):
        """Test the multiset initializer"""
        b = Multiset('abracadabra')
        self.assertTrue(b.count('a') == 5)
        self.assertTrue(b.count('b') == 2)
        self.assertTrue(b.count('r') == 2)
        self.assertTrue(b.count('c') == 1)
        self.assertTrue(b.count('d') == 1)
        b2 = Multiset(b)
        self.assertTrue(b2 == b)

    def test_repr(self):
        """Test that eval(repr(self)) == self"""
        ms = Multiset()
        self.assertTrue(ms == eval(repr(ms)))
        ms = Multiset('abracadabra')
        self.assertTrue(ms == eval(repr(ms)))

    def test_str(self):
        abra = Multiset('abracadabra')
        self.assertSequenceEqual(str(Multiset()), 'Multiset()')
        self.assertTrue("'a'^5" in str(abra))
        self.assertTrue("'b'^2" in str(abra))
        self.assertTrue("'c'" in str(abra))
        abra_elems = set(("'a'^5", "'b'^2", "'r'^2", "'c'", "'d'"))
        assert compare_Multiset_string(Multiset('abracadabra')) == abra_elems

    def test_count(self):
        """Check that we record the correct number of elements."""
        ms = Multiset('abracadabra')
        self.assertEqual(5, ms.count('a'))
        self.assertEqual(0, ms.count('x'))

    def test_nlargest(self):
        abra = Multiset('abracadabra')
        sort_key = lambda e: (-e[1], e[0])
        abra_counts = [('a', 5), ('b', 2), ('r', 2), ('c', 1), ('d', 1)]
        self.assertEqual(sorted(abra.nlargest(), key=sort_key), abra_counts)
        self.assertEqual(sorted(abra.nlargest(3), key=sort_key), abra_counts[:3])
        self.assertEqual(Multiset('abcaba').nlargest(3), [('a', 3), ('b', 2), ('c', 1)])

    def test_from_map(self):
        """Check that we can form a multiset from a map."""
        frommap = Multiset._from_map({'a': 1, 'b': 2})
        fromit = Multiset(('a', 'b', 'b'))
        self.assertEqual(frommap, fromit)

    def test_copy(self):
        """Check that we can copy multisets"""
        empty = Multiset()
        self.assertTrue(empty.copy() == empty)
        self.assertTrue(empty.copy() is not empty)
        abc = Multiset('abc')
        self.assertTrue(abc.copy() == abc)
        self.assertTrue(abc.copy() is not abc)

    def test_len(self):
        """Check the number of elements in our multisets."""
        self.assertEqual(0, len(Multiset()))
        self.assertEqual(3, len(Multiset('abc')))
        self.assertEqual(4, len(Multiset('aaba')))

    def test_contains(self):
        """Verify that we can test if an object is a member of a multiset."""
        self.assertTrue('a' in Multiset('bbac'))
        self.assertFalse('a' in Multiset())
        self.assertFalse('a' in Multiset('missing letter'))

    def test_le(self):
        self.assertTrue(Multiset() <= Multiset())
        self.assertTrue(Multiset() <= Multiset('a'))
        self.assertTrue(Multiset('abc') <= Multiset('aabbbc'))
        self.assertFalse(Multiset('abbc') <= Multiset('abc'))
        with self.assertRaises(TypeError):
            Multiset('abc') < set('abc')
        self.assertFalse(Multiset('aabc') < Multiset('abc'))

    def test_hash(self):
        bag_with_empty_tuple = Multiset([()])
        self.assertFalse(hash(Multiset()) == hash(bag_with_empty_tuple))
        self.assertFalse(hash(Multiset()) == hash(Multiset((0,))))
        self.assertFalse(hash(Multiset('a')) == hash(Multiset(('aa'))))
        self.assertFalse(hash(Multiset('a')) == hash(Multiset(('aaa'))))
        self.assertFalse(hash(Multiset('a')) == hash(Multiset(('aaaa'))))
        self.assertFalse(hash(Multiset('a')) == hash(Multiset(('aaaaa'))))
        self.assertTrue(hash(Multiset('ba')) == hash(Multiset(('ab'))))
        self.assertTrue(hash(Multiset('badce')) == hash(Multiset(('dbeac'))))

    def test_num_unique_elems(self):
        assert Multiset('abracadabra').num_unique_elements() == 5

    def test_keying(self):
        """
        Since Multiset is mutable and FronzeMultiset is hashable, the second
        should be usable for dictionary keys and the second should raise a key
        or value error when used as a key or placed in a set.
        """
        b = Multiset([1, 1, 2, 3])  # prototypical frozen multiset.

        c = Multiset([4, 4, 5, 5, b, b])  # make sure we can nest them
        d = Multiset([4, Multiset([1, 3, 2, 1]), 4, 5, b, 5])
        self.assertEqual(c, d) # Make sure both constructions work.

        dic = {}
        dic[b] = 3
        dic[c] = 5
        dic[d] = 7
        self.assertEqual(len(dic), 2) # Make sure no duplicates in dictionary.

        # test commutativity of multiset instantiation.
        self.assertEqual(Multiset([4, 4, 5, 5, c]), Multiset([4, 5, d, 4, 5]))

    def test_split(self):
        """Test that we can split the multiset into elements and counts"""
        abra = Multiset("abracadabra")
        y, d = abra.split()
        for el in y:
            self.assertEqual(abra.count(el), d[y.index(el)])

    def test_degeneracy(self):
        abra = Multiset("abracadabra")
        self.assertEqual(120*2*2, abra.degeneracy())

if __name__ == '__main__':
    unittest.main()

