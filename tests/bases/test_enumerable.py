import unittest

from collections import Counter  # Avoid using Multiset
from fractions import Fraction  # for TypeCheck

from funcstructs.bases.enumerable import Enumerable, typecheck


# Temporary classes


class IntEnum1(Enumerable):
    def __init__(self, n):
        self.n = n

    def __iter__(self):
        return iter(range(self.n))


class IntEnum2(Enumerable):
    def __init__(self, n):
        self.n = n

    def __iter__(self):
        return iter(range(self.n))


class IntPartEnum(Enumerable):
    def __init__(self, n, part=None):
        self.n = n
        if part is not None:
            part = tuple(sorted(part))
        self.part = part

    def __iter__(self):
        if self.part is not None:
            for i in range(self.n):
                for j in range(self.n):
                    yield i, j
        else:
            for i in range(self.n):
                for j in range(self.part):
                    yield i, j


class PartPartEnum(Enumerable):
    def __init__(self, part1, part2):
        if len(part1) != len(part2):
            raise TypeError
        self.part1 = tuple(part1)
        self.part2 = tuple(part2)

    def __iter__(self):
        return iter(zip(part1, part2))


class EnumerableTests(unittest.TestCase):

    enumerators = [IntEnum1, IntEnum2, IntPartEnum, PartPartEnum]
    enumerations = []
    for i in range(3, 10):
        enumerations.append(IntEnum1(i))
        enumerations.append(IntEnum2(i))
        enumerations.append(IntPartEnum(i))
        enumerations.append(IntPartEnum(i, [2, 3, 5]))
        enumerations.append(PartPartEnum(range(-1, i), "abcdefghijk"[:i+1]))

    def test_repr(self):
        """Test each enumerator correctly represents itself"""
        for enum in self.enumerations:
            self.assertEqual(enum, eval(repr(enum)))

    def test_eq(self):
        """Test each enumeration is unique"""
        for i, e1 in enumerate(self.enumerations):
            for j, e2 in enumerate(self.enumerations):
                if i == j:
                    self.assertEqual(e1, e2)
                else:
                    self.assertNotEqual(e1, e2)

    def test_hashability(self):
        """Test the hash equivalence relation."""
        for e1 in self.enumerations:
            for e2 in self.enumerations:
                if e1 == e2:
                    self.assertEqual(hash(e1), hash(e2))

    def test_as_keys(self):
        """Test that each item may be used as a key."""
        d = dict((y, x) for x, y in enumerate(self.enumerations))
        self.assertEqual(len(self.enumerations), len(d))
        s1 = IntEnum1(5)
        s2 = PartPartEnum(range(-1, 5), "abcdef")
        i1 = d[s1]
        i2 = d[s2]
        d[IntEnum1(5)] = -7
        d[PartPartEnum(part2="abcdef", part1=range(-1, 5))] += 27
        self.assertEqual(-7, d[s1])
        self.assertEqual(i2+27, d[s2])

    def test_write_once(self):
        """Test weather attribute creation and deletion is blocked"""
        t = IntPartEnum(part=[4, 5, 6], n=7)
        with self.assertRaises(AttributeError):
            t.n = "a"
        with self.assertRaises(AttributeError):
            t.part = (6, 7)
        with self.assertRaises(AttributeError):
            del t.n
        with self.assertRaises(AttributeError):
            del t.part
        with self.assertRaises(AttributeError):
            t.n += 1
        self.assertEqual([7, (4, 5, 6)], [t.n, t.part])

    def test_typecheck(self):
        """Test type check tests proper types."""

        class IntCutoff(object):
            def __init__(self, cutoff):
                self.cutoff = cutoff

            @typecheck(int)
            def __contains__(self, other):
                """Test for an int."""
                return other > self.cutoff

        class NumCutoff(object):
            def __init__(self, cutoff):
                self.cutoff = cutoff

            @typecheck(int, float)
            def __contains__(self, other):
                """Test for a number."""
                return other > self.cutoff

        class sint(int):
            pass  # test instances of subclass

        self.assertEqual(IntCutoff.__contains__.__doc__, "Test for an int.")
        self.assertEqual(NumCutoff.__contains__.__doc__, "Test for a number.")
        self.assertEqual(IntCutoff.__contains__.__name__, "__contains__")
        self.assertEqual(NumCutoff.__contains__.__name__, "__contains__")

        cutoffs = [4, 7]
        intobjs = list(map(IntCutoff, cutoffs))
        numobjs = list(map(NumCutoff, cutoffs))

        for i in range(10):
            for cutoff, intobj, numobj in zip(cutoffs, intobjs, numobjs):
                self.assertNotIn(Fraction(i), intobj)
                self.assertNotIn(Fraction(i), numobj)
                if i > cutoff:
                    self.assertIn(i, intobj)
                    self.assertIn(i, numobj)
                    self.assertIn(sint(i), intobj)
                    self.assertIn(sint(i), numobj)
                    self.assertNotIn(1.*i, intobj)
                    self.assertIn(1.*i, numobj)
                else:
                    self.assertNotIn(i, intobj)
                    self.assertNotIn(i, numobj)
                    self.assertNotIn(sint(i), intobj)
                    self.assertNotIn(sint(i), numobj)
                    self.assertNotIn(1.*i, intobj)
                    self.assertNotIn(1.*i, numobj)
