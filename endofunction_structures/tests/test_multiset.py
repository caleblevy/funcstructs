import unittest
import collections
import random

from ..multiset import Multiset


def string_components(b):
    """Compare multiset strings."""
    return set(str(b).lstrip('{').rstrip('}').split(', '))


class MultisetTests(unittest.TestCase):

    abra = Multiset("abracadabra")
    nest = Multiset([1, 2, 2, 3, 3, abra, abra])
    empty = Multiset()
    nest2 = Multiset([nest, empty, 4])

    msets = [abra, nest, empty, nest2]

    def test_init(self):
        """Test the multiset initializer"""
        mcounts = [
            {'a': 5, 'b': 2, 'r': 2, 'c': 1, 'd': 1},
            {1: 1, 2: 2, 3: 2, self.abra: 2},
            {},
            {self.nest: 1, self.empty: 1, 4: 1}
        ]
        for count, mset in zip(mcounts, self.msets):
            for el, mult in count.items():
                self.assertEqual(mult, mset[el])
                # Ensure multisets return themselves
                self.assertEqual(mult, Multiset(mset)[el])

    def test_repr(self):
        """Test that eval(repr(self)) == self"""
        for mset in self.msets:
            self.assertEqual(mset, eval(repr(mset)))

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

    def test_str(self):
        """Test string behaves according to specification"""
        self.assertSequenceEqual('Multiset()', str(self.empty))
        self.assertEqual(
            {"'a'^5", "'b'^2", "'r'^2", "'c'", "'d'"},
            string_components(self.abra)
        )

    def test_keying(self):
        """Check that we record the correct number of elements."""
        ms = Multiset('abracadabra')
        self.assertEqual(5, ms['a'])
        with self.assertRaises(KeyError):
            self.assertEqual(0, ms['x'])

    def test_most_common(self):
        """Test inherited method most_common behaves correctly"""
        a = collections.Counter(list(self.abra))
        b = collections.Counter(list(self.nest))
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

    def test_dict_methods(self):
        """Test that the keys, values and items methods are unaffected by
        overridden iter."""
        for mset, items_count in zip(self.msets, [5, 4, 0, 3]):
            self.assertEqual(items_count, len(mset.values()))
            self.assertEqual(items_count, len(mset.items()))
            self.assertEqual(items_count, len(mset.keys()))
            self.assertEqual(items_count, len(set(mset.items())))
            self.assertEqual(items_count, len(set(mset.keys())))

    def test_contains(self):
        """Verify that we can test if an object is a member of a multiset."""
        self.assertIn('a', Multiset('bbac'))
        self.assertNotIn('a', Multiset())
        self.assertNotIn('a', Multiset('missing letter'))

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

    def test_immutability(self):
        """Test that all inherited mutating methods have been disabled."""
        abra = self.abra
        with self.assertRaises(TypeError):
            abra['a'] += 1
        with self.assertRaises(TypeError):
            abra['b'] = 2
        with self.assertRaises(TypeError):
            del abra['b']
        with self.assertRaises(TypeError):
            abra.clear()
        with self.assertRaises(TypeError):
            abra.pop('a')
        with self.assertRaises(TypeError):
            abra.popitem()
        with self.assertRaises(TypeError):
            abra.setdefault('f', 1)
        with self.assertRaises(TypeError):
            abra.update(abra)
        self.assertEqual(Multiset('abracadabra'), abra)

    def test_split(self):
        """Test that the indices of elements and multiplicities correspond."""
        for mset in self.msets:
            y, d = mset.split()
            for i, el in enumerate(y):
                self.assertEqual(mset[el], d[i])

    def test_degeneracy(self):
        """Test multiset degeneracies reflect multiset permutations"""
        for mset, deg in zip(self.msets, [120*2*2, 2*2*2, 1, 1]):
            self.assertEqual(deg, mset.degeneracy())
