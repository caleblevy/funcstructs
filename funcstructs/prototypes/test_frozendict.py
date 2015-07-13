"""Tests of immutable mapping.

Caleb Levy, 2015.
"""

from __future__ import print_function

import unittest
from collections import Counter, Mapping, MutableMapping

from frozendict import frozendict


class FrozendictClassTests(unittest.TestCase):

    def test_frozendict_type(self):
        """Ensure type(frozendict) is type"""
        self.assertIs(type(frozendict), type)
        self.assertTrue(issubclass(frozendict, Mapping))
        self.assertFalse(issubclass(frozendict, MutableMapping))
        self.assertIsInstance(frozendict(), Mapping)
        self.assertNotIsInstance(frozendict(), MutableMapping)

    def test_slots_are_hidden(self):
        """Make sure no trace of internal map is present."""
        self.assertFalse(hasattr(frozendict, '__slots__'))
        self.assertFalse(hasattr(frozendict, '_mapping'))
        self.assertNotIn('__slots__', frozendict.__dict__)
        self.assertNotIn('_mapping', frozendict.__dict__)
        self.assertNotIn('__slots__', dir(frozendict))
        self.assertNotIn('_mapping', dir(frozendict))
        self.assertNotIn('__slots__', dir(frozendict()))
        self.assertNotIn('_mapping', dir(frozendict()))


class FrozendictTests(unittest.TestCase):

    class F(frozendict):
        pass

    a = {'a': 1, 'b': 2, 'c': 3}
    b = frozendict({'a': 1, 'b': 2, 'c': 3})
    c = F(b)
    e = frozendict({1: [1, 2, 3], 2: (1, 2, 3)})
    f = frozendict({b: 14, 1: 15})
    dicts = [a, b, c, e, f]

    def test_constructors(self):
        """Test frozendict works with usual constructors"""
        kwargs = {'c': 3, 'd': 4, 'e': 5}
        for fdclass in [frozendict, self.F]:
            self.assertEqual(
                {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5},
                dict(fdclass(a=1, b=2, **kwargs))
            )
            self.assertEqual(
                {1: 1, 2: 2, 3: 3, 4: 4, 5: 5},
                dict(fdclass(enumerate(range(1, 6), start=1)))
            )
            self.assertEqual(
                fdclass.fromkeys([1, 2, 3], None),
                fdclass({1: None, 2: None, 3: None})
            )

    def test_equality(self):
        """Tests two mappings compare equal iff their key value pairs are."""
        for d1 in self.dicts:
            for d2 in self.dicts:
                if dict(d1) == dict(d2):
                    self.assertEqual(d1, d2)
                else:
                    self.assertNotEqual(d1, d2)
        t = {'d': 1, 'e': 2, 'a': 3}
        dtypes = [t, frozendict(t), self.F(t)]
        for d1 in dtypes:
            for d2 in dtypes:
                self.assertEqual(d1, d2)

    def test_immutability(self):
        """Test that all inherited mutating methods have been disabled."""
        for d in [self.b, self.c]:
            d_backup = d
            with self.assertRaises((TypeError, AttributeError)):
                d['a'] += 1
            with self.assertRaises((TypeError, AttributeError)):
                d['b'] = 2
            with self.assertRaises((TypeError, AttributeError)):
                del d['b']
            with self.assertRaises((TypeError, AttributeError)):
                d.clear()
            with self.assertRaises((TypeError, AttributeError)):
                d.pop('a')
            with self.assertRaises((TypeError, AttributeError)):
                d.popitem()
            with self.assertRaises((TypeError, AttributeError)):
                d.setdefault('f', 1)
            with self.assertRaises((TypeError, AttributeError)):
                d.update({'d': 4})
            self.assertEqual(d.__class__({'a': 1, 'b': 2, 'c': 3}), d)
            self.assertIs(d, d_backup)

    def test_repr(self):
        """Ensure fronzendicts evaluate to themselves"""
        for d in self.dicts:
            d_from_repr = eval(repr(d), {d.__class__.__name__: type(d)})
            self.assertEqual(d, d_from_repr)
            self.assertIs(type(d), type(d_from_repr))

    def test_hash(self):
        """Test that frozendicts with hashable keys are hashable"""
        class TypeEqFrozendict(frozendict):
            def __eq__(self, other):
                if type(self) is type(other):
                    return frozendict.__eq__(self, other)
                return False
            __hash__ = frozendict.__hash__

        a = frozendict(a=1, b=2, c=3)
        b = TypeEqFrozendict(a=1, b=2, c=3)

        dic = {}
        dic[a] = 1
        dic[b] = 2
        self.assertEqual(len(dic), 2)
        dic[a] += 3
        self.assertEqual(dic[a], 4)
        self.assertEqual(set(dic), {a, b})

    def test_method_independence(self):
        """Test overriding one method does not affect another."""
        class Multiset(frozendict):
            def __iter__(self):
                for el, mult in self.items():
                    for _ in range(mult):
                        yield el

        mset = Multiset({'a': 1, 'b': 3})
        c = sorted(mset)
        self.assertEqual(c, ['a', 'b', 'b', 'b'])
        self.assertEqual(Counter(c), dict(mset))

    def test_copy(self):
        """Test that frozendict copies internal dict."""
        a = frozendict({1: 'a', 2: 'b'})
        b = a.copy()
        self.assertEqual(a, b)
        b[1] = 'a'
        self.assertEqual({1: 'a', 2: 'b'}, a)  # test a independent of copy


if __name__ == '__main__':
    unittest.main()
