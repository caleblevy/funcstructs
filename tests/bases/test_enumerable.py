import unittest

from collections import Counter  # Avoid using Multiset

from funcstructs.bases.enumerable import ImmutableStruct, Enumerable


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
