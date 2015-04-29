import unittest

from ..bases import Tuple


class TupleTests(unittest.TestCase):

    class A(Tuple):
        pass

    class B(Tuple):
        pass

    class C(A):
        pass

    tup = (1, 2, 3)
    t = Tuple(tup)
    a = A(tup)
    b = B(tup)
    c = C(tup)
    tups = [tup, t, a, b, c]
    c_mirrors = list(map(C, tups))  # Test instantiation works

    def test_equality(self):
        """Test different derived classes from Tuple compare unequal"""
        q = (2, 2, 3)
        others = [q, Tuple(q), self.A(q), self.B(q), self.C(q)]
        n = len(self.tups)
        for i in range(n):
            for j in range(n):
                self.assertEqual(self.c_mirrors[i], self.c_mirrors[j])
                self.assertNotEqual(self.tups[i], others[j])
                if i == j:
                    self.assertEqual(self.tups[i], self.tups[j])
                else:
                    self.assertNotEqual(self.tups[i], self.tups[j])

    def test_disabled_operations(self):
        """Make sure Tuples cannot be added or duplicated"""
        for x in self.tups[1:]:
            # Check multiplication fails
            with self.assertRaises(TypeError):
                prod = 2 * x
            with self.assertRaises(TypeError):
                prod = x * 2
            for y in self.tups:
                with self.assertRaises(TypeError):
                    s = x + y
                with self.assertRaises(TypeError):
                    s = y + x

    def test_addition_override(self):
        class D(self.C):
            def __add__(self, other):
                return D(tuple.__add__(self, other))

            def __radd__(self, other):
                return D(tuple.__add__(other, self))

        d = D([4, 5, 6])
        self.assertEqual(D([4, 5, 6, 1, 2, 3]), d + self.c)
        self.assertEqual(D([1, 2, 3, 4, 5, 6]), self.c + d)

    def test_use_as_keys(self):
        """Ensure elements behave as expected when used as keys"""
        self.assertEqual(len(self.tups), len(set(self.tups)))
        dic = {}
        for i, el in enumerate(self.tups):
            dic[el] = i
        self.assertEqual(len(self.tups), len(dic))
        dic[self.C([1, 2, 3])] = 'a'
        self.assertEqual(len(self.tups), len(dic))
        self.assertEqual(dic[self.c], 'a')

    def test_slotted(self):
        """Make sure Tuples have __slots__ and don't have __dict__."""
        self.assertTrue(hasattr(self.t, '__slots__'))
        self.assertFalse(hasattr(self.t, '__dict__'))
