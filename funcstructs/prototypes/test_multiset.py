import unittest
import random
from collections import Counter
from itertools import product

from multiset import Multiset, counts


class MultisetTests(unittest.TestCase):
    abra = Multiset("abracadabra")
    nest = Multiset([1, 2, 2, 3, 3, abra, abra])
    empty = Multiset()
    nest2 = Multiset([nest, empty, 4])

    msets = [abra, nest, empty, nest2]

    def test_constructor(self):
        """Test the multiset initializer"""
        mcounts = [
            {'a': 5, 'b': 2, 'r': 2, 'c': 1, 'd': 1},
            {1: 1, 2: 2, 3: 2, self.abra: 2},
            {},
            {self.nest: 1, self.empty: 1, 4: 1}
        ]
        for c, m in zip(mcounts, self.msets):
            self.assertEqual(c, dict(m))
            # Multiset should accept dicts
            self.assertEqual(c, dict(Multiset(dict(m))))
            # Multiset should be idempotent
            self.assertEqual(c, dict(Multiset(m)))
        count = Counter("abracadabra")
        # Test Multiset DOES work with keywords
        self.assertEqual(Multiset(count), Multiset(a=5, b=2, r=2, c=1, d=1))
        self.assertEqual(Multiset(count), Multiset(**count))
        # Test that special keywords are not forbidden
        self.assertEqual(
            dict(args=1, kwargs=1, self=1, cls=1, iterable=1),
            dict(Multiset(args=1, kwargs=1, self=1, cls=1, iterable=1))
        )

        # Test Multiset rejects inappropriate maps.
        count['a'] = 0
        with self.assertRaises(TypeError):
            m = Multiset(count)
        count['a'] -= 1
        with self.assertRaises(TypeError):
            m = Multiset(count)
        count['a'] = 1.
        with self.assertRaises(TypeError):
            m = Multiset(count)
        # Multiset, like dict, (and like Counter probably should), rejects None
        with self.assertRaises(TypeError):
            Multiset(None)
        # Test that __new__ requires a subclass of Multiset
        with self.assertRaises((TypeError, ValueError, IndexError)):
            Multiset.__new__()
        # Test that we cannot mix iterables and keywords
        with self.assertRaises(TypeError):
            Multiset([1, 1, 2], a=3)
        with self.assertRaises(TypeError):
            Multiset({1: 2}, a=3)

    def test_repr(self):
        """Test that eval(repr(self)) == self"""
        # Need to test outside frozendict due to overridden __repr__
        for mset in self.msets:
            m_from_repr = eval(repr(mset))
            self.assertEqual(mset, m_from_repr)
            self.assertEqual(m_from_repr, mset)
            self.assertIs(type(mset), type(m_from_repr))

    def test_equality(self):
        """Test Multisets are equal iff their elements are equal"""
        for i, ms1 in enumerate(self.msets):
            mdup = list(ms1)
            # Test subsets do not compare equal
            if mdup:
                mdup.append(mdup[0])
                self.assertNotEqual(ms1, Multiset(mdup))
            for j, ms2 in enumerate(self.msets):
                if i == j:
                    self.assertEqual(ms1, ms2)
                else:
                    self.assertNotEqual(ms1, ms2)

    def test_most_common(self):
        """Test inherited method most_common behaves correctly"""
        # Needed to test methods are not broken from overridden __iter__
        a = Counter(list(self.abra))
        b = Counter(list(self.nest))
        self.assertEqual(a.most_common(1), self.abra.most_common(1))
        self.assertEqual(
            set(a.most_common()[1:3]),
            set(self.abra.most_common()[1:3])
        )
        self.assertEqual(
            set(b.most_common(3)),
            set(self.nest.most_common(3))
        )

    def test_len(self):
        """Check number of elements in our multisets including multiplicity."""
        for mset, count in zip(self.msets, [11, 7, 0, 3]):
            self.assertEqual(count, len(mset))
            self.assertEqual(count, len(list(mset)))

    def test_shuffling_invarience(self):
        """Test Multisets and hashes are invarient under element shuffling"""
        for mset in self.msets:
            shuffled = list(mset)
            random.shuffle(shuffled)
            self.assertEqual(mset, Multiset(shuffled))
            self.assertEqual(hash(mset), hash(Multiset(shuffled)))

    def test_keyability(self):
        """Check that Multisets can be properly used as keys"""
        dic = {}
        for i, mset in enumerate(self.msets):
            dic[mset] = i
        self.assertEqual(4, len(dic))
        dic[Multiset("baracadabra")] = -7
        self.assertEqual(4, len(dic))
        self.assertEqual(-7, dic[self.abra])
        dic[7] = 42
        self.assertEqual(5, len(set(dic)))

    def test_counts(self):
        """Test that the indices of elements and multiplicities correspond."""
        for mset in self.msets:
            y, d = counts(mset)
            for i, el in enumerate(y):
                self.assertEqual(mset[el], d[i])

    def test_degeneracy(self):
        """Test multiset degeneracies reflect multiset permutations"""
        for mset, deg in zip(self.msets, [120*2*2, 2*2*2, 1, 1]):
            self.assertEqual(deg, mset.degeneracy())

    def assertTypeEqual(self, first, second, msg=None):
        """Succeed if two objects are equal and have the same type."""
        self.assertIs(type(first), type(second), msg)
        self.assertEqual(first, second, msg)

    def test_binary_operations(self):
        """Test '+', '&', '|' and '-' for Multisets and Counters."""
        i1, i2, i3 = tuple("aaabbc"), tuple("abcd"), tuple([1])
        # We want to test our multiset operations on every ordered pair from
        # {Multiset(a), Counter(a), Multiset(b), Counter(b)} for every
        # combination with replacement of a and b chosen from {i1, i2, i3}.
        for l, r in product([Multiset, Counter], repeat=2):
            for a, b in product([i1, i2, i3], repeat=2):
                self.assertEqual(l(a+b), l(a) + r(b))
                if {a, b} == {i1, i2}:  # sets with nonempty differences
                    self.assertTypeEqual(
                        l("aab" if a == i1 else "d"),
                        l(a) - r(b)
                    )
                    self.assertTypeEqual(l("abc"), l(a) & r(b))
                    self.assertTypeEqual(l("aaabbcd"), l(a) | r(b))
                elif {a, b} in ({i1, i3}, {i2, i3}):  # sets are disjoint
                    self.assertTypeEqual(l(a), l(a) - r(b))
                    self.assertTypeEqual(l(), l(a) & r(b))
                    self.assertTypeEqual(l(a + b), l(a) | r(b))
                else:  # one set contains the other
                    self.assertTypeEqual(l(), l(a) - r(b))
                    self.assertTypeEqual(l(a), l(a) & r(b))
                    self.assertTypeEqual(l(a), l(a) | r(b))


if __name__ == '__main__':
    unittest.main()
