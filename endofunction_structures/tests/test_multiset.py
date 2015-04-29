import unittest

from ..multiset import Multiset


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
        self.assertTrue(b['a'] == 5)
        self.assertTrue(b['b'] == 2)
        self.assertTrue(b['r'] == 2)
        self.assertTrue(b['c'] == 1)
        self.assertTrue(b['d'] == 1)
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
        self.assertEqual(compare_Multiset_string(Multiset('abracadabra')),
                         abra_elems)

    def test_count(self):
        """Check that we record the correct number of elements."""
        ms = Multiset('abracadabra')
        self.assertEqual(5, ms['a'])
        with self.assertRaises(KeyError):
            self.assertEqual(0, ms['x'])

    def test_most_common(self):
        abra = Multiset('abracadabra')
        abra_counts = [('a', 5), ('b', 2), ('r', 2), ('c', 1), ('d', 1)]
        self.assertEqual(
            sorted(abra.most_common(), key=lambda e: (-e[1], e[0])),
            abra_counts
        )
        self.assertEqual(
            sorted(abra.most_common(3), key=lambda e: (-e[1], e[0])),
            abra_counts[:3]
        )
        self.assertEqual(Multiset('abcaba').most_common(3),
                         [('a', 3), ('b', 2), ('c', 1)])

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

    def test_hash(self):
        bag_with_empty_tuple = Multiset([()])
        self.assertEqual(hash(bag_with_empty_tuple), hash(Multiset([()])))
        self.assertEqual(hash(Multiset('aabc')), hash(Multiset('baca')))
        self.assertEqual(hash(Multiset('ba')), hash(Multiset(('ab'))))
        self.assertEqual(hash(Multiset('badce')), hash(Multiset(('dbeac'))))

    def test_keyability(self):
        """
        Since Multiset is mutable and FronzeMultiset is hashable, the second
        should be usable for dictionary keys and the second should raise a key
        or value error when used as a key or placed in a set.
        """
        b = Multiset([1, 1, 2, 3])  # prototypical frozen multiset.

        c = Multiset([4, 4, 5, 5, b, b])  # make sure we can nest them
        d = Multiset([4, Multiset([1, 3, 2, 1]), 4, 5, b, 5])
        self.assertEqual(c, d)  # Make sure both constructions work.

        dic = {}
        dic[b] = 3
        dic[c] = 5
        dic[d] = 7
        self.assertEqual(len(dic), 2)  # Make sure no duplicates in dictionary.

        # Test commutativity of multiset instantiation.
        self.assertEqual(Multiset([4, 4, 5, 5, c]), Multiset([4, 5, d, 4, 5]))

    def test_immutability(self):
        """Test that all inherited mutating methods have been disabled."""
        abra = Multiset('abracadabra')
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
        """ Test that the indices of the elements and multiplicities
        correspond. """
        abra = Multiset("abracadabra")
        y, d = abra.split()
        for el in y:
            self.assertEqual(abra[el], d[y.index(el)])

    def test_degeneracy(self):
        abra = Multiset("abracadabra")
        self.assertEqual(120*2*2, abra.degeneracy())

    def test_from_map(self):
        """Check that we can form a multiset from a map."""
        fromit = Multiset(('a', 'b', 'b'))
        frommap = Multiset(fromit)
        self.assertEqual(frommap, fromit)
