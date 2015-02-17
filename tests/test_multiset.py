import unittest
from endofunction_structures.multiset import *


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
        self.assertEqual(compare_Multiset_string(Multiset('abracadabra')),
                         abra_elems)

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
        self.assertEqual(sorted(abra.nlargest(3), key=sort_key), 
                         abra_counts[:3])
        self.assertEqual(Multiset('abcaba').nlargest(3),
                         [('a', 3), ('b', 2), ('c', 1)])

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