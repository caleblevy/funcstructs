import unittest

from ... import(
    TreeEnumerator, ForestEnumerator, PartitionForests,
    EndofunctionStructures, TransformationMonoid,
    FixedContentNecklaces
)

from ...multiset import Multiset
from .. import Enumerable


class EnumerableTests(unittest.TestCase):

    enums = []
    for n in {4, 5}:
        enums.append(TreeEnumerator(n))
        enums.append(ForestEnumerator(n))
        enums.append(TransformationMonoid(n))
        enums.append(EndofunctionStructures(n))
    enums.extend([
        EndofunctionStructures(100, [3, 3, 2]),
        EndofunctionStructures(100, [1, 1, 2, 3])
    ])
    enums.extend([
        FixedContentNecklaces([3, 3, 2]),
        FixedContentNecklaces([1, 2, 1, 3]),
        PartitionForests([3, 3, 2]),
        PartitionForests([1, 3, 2, 1])
    ])

    def test_abstract_methods(self):
        """Check abstract overrides require overriding to instantiate"""
        class NoInit(Enumerable):
            def __iter__(self):
                return iter(range(self.n))

        class NoIter(Enumerable):
            def __new__(cls, n):
                return super(NoIter, cls).__new__(cls, n=n)

        class Init(NoInit):
            def __new__(cls, n):
                return super(Init, cls).__new__(cls, n=n)

        class Iter(NoIter):
            def __iter__(self):
                return iter(range(self.n))

        # Test that both __init__ and __iter__ are required
        with self.assertRaises(TypeError):
            Enumerable(4, [1, 2, 3])
        with self.assertRaises(TypeError):
            list(NoInit(4))
        with self.assertRaises(TypeError):
            list(NoIter(4))
        # Test filling in the methods stops the erro
        self.assertEqual(4, len(list(Init(4))))
        self.assertEqual(4, len(list(Iter(4))))

    def test_repr(self):
        """Test each enumerator correctly represents itself"""
        for enum in self.enums:
            self.assertEqual(enum, eval(repr(enum)))

    def test_eq(self):
        """Test each enumeration is unique"""
        for i, e1 in enumerate(self.enums):
            for j, e2 in enumerate(self.enums):
                if i == j:
                    self.assertEqual(e1, e2)
                else:
                    self.assertNotEqual(e1, e2)

    def test_hashability(self):
        """test each enum can be used as a unique hash"""
        dic = {}
        for i, e in enumerate(self.enums):
            dic[e] = i
        elen = len(dic)
        dic[EndofunctionStructures(100, [3, 3, 2])] = -2100
        self.assertEqual(elen, len(dic))
        self.assertIn(-2100, dic.values())
        dic[EndofunctionStructures(10)] = 1
        self.assertEqual(elen+1, len(set(dic)))

    def test_lower_bounds(self):
        """Ensure that negative enumerations raise errors"""
        with self.assertRaises(ValueError):
            TreeEnumerator(0)
        with self.assertRaises(ValueError):
            ForestEnumerator(-1)
        with self.assertRaises(ValueError):
            TransformationMonoid(-1)
        with self.assertRaises(ValueError):
            EndofunctionStructures(-1)
