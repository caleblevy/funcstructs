#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright © 2009 Michael Lenzen <m.lenzen@gmail.com>
#
""" multiset - Also known as a bag or unordered tuple.

This module provides three classes:
    basemultiset - The superclass of multiset and frozen multiset. It is both
        immutable and unhashable.
    multiset - A mutable (unhashable) multiset.
    frozenmultiset - A hashable (immutable) multiset.
"""

import heapq
from collections import MutableSet, Set, Hashable
from operator import itemgetter
import unittest


class BaseMultiset(Set):
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
            for elem in iterable:
                self._inc(elem)

    def __repr__(self):
        """
        The string representation is a call to the constructor given a tuple 
        containing all of the elements.

        This runs in whatever tuple(self) does, I'm assuming O(len(self))
        """
        if self._size == 0:
            return '{0}()'.format(self.__class__.__name__)
        else:
            format_string = '{class_name}({tup!r})'
            return format_string.format(class_name=self.__class__.__name__, 
                                        tup=tuple(self))

    def __str__(self):
        """
        The printable string appears just like a set, except that each element
        is raised to the power of the multiplicity if it is greater than 1.

        This runs in O(self.num_unique_elements())
        """
        if self._size == 0:
            return '{}'
        else:
            format_single = '{elem!r}'
            format_mult = '{elem!r}^{mult}'
            strings = []
            for elem, mult in self._dict.items():
                if mult > 1:
                    strings.append(format_mult.format(elem=elem, mult=mult))
                else:
                    strings.append(format_single.format(elem=elem))
            strings = tuple(strings)
            string = '{first}'.format(first=strings[0])
            for i in range(1,len(strings)):
                string = '{prev}, {next}'.format(prev=string, next=strings[i])
            string = '{{{0}}}'.format(string)
            return string

    ## Internal methods

    def _set(self, elem, value):
        """Set the multiplicity of elem to count.

        This runs in O(1) time
        """
        if value < 0:
            raise ValueError
        old_count = self.multiplicity(elem)
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
        self._set(elem, self.multiplicity(elem) + count)

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

    def multiplicity(self, elem):
        """
        Return the multiplicity of elem. If elem is not in the set no Error is
        raised, instead 0 is returned.

        This runs in O(1) time
        """
        return self._dict.get(elem, 0)
    
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
    def _from_map(cls, map):
        """
        Creates a multiset from a dict of elem->count. Each key in the dict is
        added if the value is > 0.

        This runs in O(len(map))
        """
        out = cls()
        for elem, count in map.items():
            out._inc(elem, count)
        return out

    def copy(self):
        "Create a shallow copy of self in O(len(self.num_unique_elements()))."
        return self._from_map(self._dict)
    
    ## implementing Sized methods

    def __len__(self):
        """ Returns the cardinality of the multiset. This runs in O(1)."""
        return self._size

    ## implementing Container methods

    def __contains__(self, elem):
        """Returns the multiplicity of the element. This runs in O(1)."""
        return self.multiplicity(elem)

    ## implementing Iterable methods

    def __iter__(self):
        """Iterate through all elements; return multiple copies if present."""
        for elem, count in self._dict.items():
            for i in range(count):
                yield(elem)

    # Comparison methods

    def __le__(self, other):
        """

        This runs in O(l + n) where:
            n is self.num_unique_elements()
            if other is a multiset:
                l = 1
            else:
                l = len(other)

        TODO write test cases for __le__
        """
        if not isinstance(other, BaseMultiset):
            raise TypeError("Cannot compare Multiset with another type.")
        if len(self) > len(other):
            return False
        for elem in self.unique_elements():
            if self.multiplicity(elem) > other.multiplicity(elem):
                return False
        return True

    def __lt__(self, other):
        return self <= other and len(self) < len(other)

    def __gt__(self, other):
        return other < self

    def __ge__(self, other):
        return other <= self

    def __eq__(self, other):
        if not isinstance(other, BaseMultiset):
            return False
        return len(self) == len(other) and self <= other

    def __ne__(self, other):
        return not (self == other)

    # Operations - &, |, +, -, ^, * and isdisjoint

    def __and__(self, other):
        """ Intersection is the minimum of corresponding counts. 

        This runs in O(l + n) where:
            n is self.num_unique_elements()
            if other is a multiset:
                l = 1
            else:
                l = len(other)

        TODO write unit tests for and
        """
        if not isinstance(other, BaseMultiset):
            other = self._from_iterable(other)
        values = dict()
        for elem in self._dict:
            values[elem] = min(other.multiplicity(elem),
                               self.multiplicity(elem))
        return self._from_map(values)

    def isdisjoint(self, other):
        """

        This runs in O(l + m*n) where:
            m is self.num_unique_elements()
            n is other.num_unique_elements()
            if other is a multiset:
                l = 1
            else:
                l = len(other)

        TODO write unit tests for isdisjoint
        """
        for value in other:
            if value in self:
                return False
        return True

    def __or__(self, other):
        """ Union is the maximum of all elements. 
        
        This runs in O(m + n) where:
            n is self.num_unique_elements()
            if other is a multiset:
                m = other.num_unique_elements()
            else:
                m = len(other)

        TODO write unit tests for or
        """
        if not isinstance(other, BaseMultiset):
            other = self._from_iterable(other)
        values = dict()
        for elem in self.unique_elements() | other.unique_elements():
            values[elem] = max(self.multiplicity(elem),
                               other.multiplicity(elem))
        return self._from_map(values)

    def __add__(self, other):
        """ Sum of sets
        other can be any iterable.
        self + other = self & other + self | other 

        This runs in O(m + n) where:
            n is self.num_unique_elements()
            m is len(other)

        TODO write unit tests for add
        """
        out = self.copy()
        for elem in other:
            out._inc(elem)
        return out

    def __sub__(self, other):
        """ Difference between the sets.
        other can be any iterable.
        For normal sets this is all s.t. x in self and x not in other. 
        For multisets this is:
           multiplicity(x) = max(0, self.multiplicity(x)-other.multiplicity(x))

        This runs in O(m + n) where:
            n is self.num_unique_elements()
            m is len(other)

        TODO write tests for sub
        """
        out = self.copy()
        for elem in other:
            try:
                out._inc(elem, -1)
            except ValueError:  # What is up with this.
                pass
        return out

    def __mul__(self, other):
        """Cartesian product of the two sets.
        other can be any iterable.
        Both self and other must contain elements that can be added together.

        This should run in O(m*n+l) where:
            m is the number of unique elements in self
            n is the number of unique elements in other
            if other is a bag:
                l is 0
            else:
                l is the len(other)
        The +l will only really matter when other is an iterable with MANY
        repeated elements.
        For example: {'a'^2} * 'bbbbbbbbbbbbbbbbbbbbbbbbbb'
        The algorithm will be dominated by counting the 'b's
        """
        if not isinstance(other, BaseMultiset):
            other = self._from_iterable(other)
        values = dict()
        for elem, count in self._dict.items():
            for other_elem, other_count in other._dict.items():
                new_elem = elem + other_elem
                new_count = count * other_count
                values[new_elem] = new_count
        return self._from_map(values)

    def __xor__(self, other):
        """ Symmetric difference between the sets. 
        other can be any iterable.

        This runs in < O(m+n) where:
            m = len(self)
            n = len(other)

        TODO write unit tests for xor
        """
        return (self - other) | (other - self)

class Multiset(BaseMultiset, MutableSet):
    """
    Multiset is a Mutable BaseMultiset, thus not hashable and unusable for dict
    keys or in other sets.
    """

    def pop(self):
        # TODO can this be done more efficiently (no need to create an 
        # iterator)?
        it = iter(self)
        try:
            value = next(it)
        except StopIteration:
            raise KeyError
        self.discard(value)
        return value

    def add(self, elem):
        self._inc(elem, 1)

    def discard(self, elem):
        try:
            self.remove(elem)
        except ValueError:
            pass

    def remove(self, elem):
        self._inc(elem, -1)

    def clear(self):
        self._dict = dict()
        self._size = 0

    # In-place operations

    def __ior__(self, other):
        """
        if isinstance(other, _basebag):
            This runs in O(other.num_unique_elements())
        else:
            This runs in O(len(other))
        """
        if not isinstance(other, BaseMultiset):
            other = self._from_iterable(other)
        for elem, other_count in other._dict.items():
            self_count = self.multiplicity(elem)
            self._set(elem, max(other_count, self_count))
        return self

    def __iand__(self, other):
        """
        if isinstance(other, _basebag):
            This runs in O(other.num_unique_elements())
        else:
            This runs in O(len(other))
        """
        if not isinstance(other, BaseMultiset):
            other = self._from_iterable(other)
        for elem, self_count in set(self._dict.items()):
            other_count = other.count(elem)
            self._set(elem, min(other_count, self_count))
        return self

    def __ixor__(self, other):
        """
        if isinstance(other, _basebag):
            This runs in O(other.num_unique_elements())
        else:
            This runs in O(len(other))
        """
        if not isinstance(other, BaseMultiset):
            other = self._from_iterable(other)
        other_minus_self = other - self
        self -= other
        self |= other_minus_self
        return self

    def __isub__(self, other):
        """
        if isinstance(it, _basebag):
            This runs in O(it.num_unique_elements())
        else:
            This runs in O(len(it))
        """
        if not isinstance(other, BaseMultiset):
            other = self._from_iterable(other)
        for elem, count in other._dict.items():
            try:
                self._inc(elem, -count)
            except ValueError:
                pass
        return self

    def __iadd__(self, other):
        """
        if isinstance(it, _basebag):
            This runs in O(it.num_unique_elements())
        else:
            This runs in O(len(it))
        """
        if not isinstance(other, BaseMultiset):
            other = self._from_iterable(other)
        for elem, count in other._dict.items():
            self._inc(elem, count)
        return self


class FrozenMultiset(BaseMultiset, Hashable):
    """
    FrozenMultiset is a Hashable BaseMultiset, thus it is immutable and usable
    for dict keys.
    """

    def __hash__(self):
        """ 
        Use the hash funtion inherited from somewhere. For now this is from
        Set, I'm not sure that it works for collections with multiple elements.

        TODO write unit tests for hash
        """
        return self._hash()


def multichoose(iterable, k):
    """
    Returns a set of all possible multisets of length k on unique elements from
    iterable. The number of sets returned is C(n+k-1, k) where:

        C is the binomial coefficient function
        n is the number of unique elements in iterable
        k is the cardinality of the resulting multisets

    The run time is O(n^min(k,n)) !!!
    DO NOT run this on big inputs.

    see http://en.wikipedia.org/wiki/Multiset#Multiset_coefficients
    """
    # if iterable is empty there are no multisets
    if not iterable:
        return set()

    symbols = set(iterable)
    
    symbol = symbols.pop()
    result = set()
    if len(symbols) == 0:
        result.add(FrozenMultiset._from_map({symbol : k}))
    else:
        for symbol_multiplicity in range(k+1):
            symbol_set = FrozenMultiset._from_map({symbol:symbol_multiplicity})
            for others in multichoose(symbols, k-symbol_multiplicity):
                result.add(symbol_set + others)
    return result


class MultisetTests(unittest.TestCase):
    """
    Test properties of Multiset objects. Tests tend to be of two forms:
        basemultiset()                     # create empty set
        basemultiset('abracadabra')        # create from an Iterable
    """

    def testMultiplicity(self):
        """Check that we record the correct number of elements."""
        ms = BaseMultiset('abracadabra')
        self.assertEqual(5, ms.multiplicity('a'))
        self.assertEqual(0, ms.multiplicity('x'))

    def testNLargest(self):
        ms = BaseMultiset('abracadabra')
        sorted_ms = [('a', 5), ('r', 2), ('b', 2), ('c', 1), ('d', 1)]
        self.assertSequenceEqual(sorted_ms, ms.nlargest())
        self.assertSequenceEqual([('a', 5), ('r', 2)], ms.nlargest(2))

    def testRepresentation(self):
        """Test that eval(repr(self)) == self"""
        ms = BaseMultiset()
        self.assertTrue(ms == eval(repr(ms)))
        ms = BaseMultiset('abracadabra')
        self.assertTrue(ms == eval(repr(ms)))

    def testStringForm(self):
        """Test str(self)."""
        self.assertEqual("{}", str(BaseMultiset()))
        ms = BaseMultiset('abracadabra')
        str_rep = "{'a'^5, 'r'^2, 'b'^2, 'c', 'd'}"
        self.assertEqual(str_rep, str(ms))

    def testFromMap(self):
        """Check that we can form a multiset from a map."""
        frommap = BaseMultiset._from_map({'a': 1, 'b': 2})
        fromit = BaseMultiset(('a', 'b', 'b'))
        self.assertEqual(frommap, fromit)

    def testCopy(self):
        """Check that we can copy multisets"""
        self.assertTrue(BaseMultiset().copy() == BaseMultiset())
        abc = BaseMultiset('abc')
        self.assertTrue(abc.copy() == abc)

    def testElementCount(self):
        """Check the number of elements in our multisets."""
        self.assertEqual(0, len(BaseMultiset()))
        self.assertEqual(3, len(BaseMultiset('abc')))
        self.assertEqual(4, len(BaseMultiset('aaba')))

    def testMemberCheck(self):
        """Verify that we can test if an object is a member of a multiset."""
        self.assertTrue('a' in BaseMultiset('bbac'))
        self.assertFalse('a' in BaseMultiset())
        self.assertFalse('a' in BaseMultiset('missing letter'))

    def testCartesianProduct(self):
        """Test a cartesian product of multisets"""
        ms = BaseMultiset('aab')

        self.assertEqual(ms * set('a'), BaseMultiset(('aa', 'aa', 'ba')))
        self.assertEqual(ms * set(), BaseMultiset())

    def testHashability(self):
        """
        Since Multiset is mutable and FronzeMultiset is hashable, the second
        should be usable for dictionary keys and the second should raise a key
        or value error when used as a key or placed in a set.
        """
        a = Multiset([1,2,3])  # Mutable multiset.
        b = FrozenMultiset([1, 1, 2, 3])  # prototypical frozen multiset.

        c = FrozenMultiset([4, 4, 5, 5, b, b])  # make sure we can nest them
        d = FrozenMultiset([4, FrozenMultiset([1, 3, 2, 1]), 4, 5, b, 5])
        self.assertEqual(c, d) # Make sure both constructions work.

        dic = {}
        dic[b] = 3
        dic[c] = 5
        dic[d] = 7
        self.assertEqual(len(dic), 2) # Make sure no duplicates in dictionary.

        with self.assertRaises(TypeError):
            dic[a] = 4
        with self.assertRaises(TypeError):
            s = set([a])
        with self.assertRaises(TypeError):
            t = FrozenMultiset([a, 1])
        with self.assertRaises(TypeError):
            w = Multiset([a,1])
        # test commutativity of multiset instantiation.
        self.assertEqual(Multiset([4, 4, 5, 5, c]), Multiset([4, 5, d, 4, 5]))

    def testMultichoose(self):
        """Test multiset enumeration."""
        self.assertEqual(set(), multichoose((), 1))  # test the empty case
        self.assertEqual({FrozenMultiset(('a',))}, multichoose('a', 1))
        self.assertEqual({FrozenMultiset(('a', 'a'))}, multichoose('a', 2))

        result = multichoose('ab', 3)
        self.assertEqual(4, len(result))
        self.assertTrue(FrozenMultiset(('a', 'a', 'a')) in result)
        self.assertTrue(FrozenMultiset(('a', 'a', 'b')) in result)
        self.assertTrue(FrozenMultiset(('a', 'b', 'b')) in result)
        self.assertTrue(FrozenMultiset(('b', 'b', 'b')) in result)

        self.assertTrue(multichoose('ab',3) == multichoose('ba',3)) # commuting


if __name__ == '__main__':
    unittest.main()