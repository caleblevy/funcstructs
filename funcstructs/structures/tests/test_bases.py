import unittest

from .. import(
    TreeEnumerator, ForestEnumerator, PartitionForests,
    EndofunctionStructures, TransformationMonoid,
    FixedContentNecklaces
)

from ..bases import Tuple, Enumerable


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
                2 * x
            with self.assertRaises(TypeError):
                x * 2
            for y in self.tups:
                with self.assertRaises(TypeError):
                    x + y
                with self.assertRaises(TypeError):
                    y + x

    def test_addition_override(self):
        """Make sure subclasses can properly override their parents' __add__"""
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

    def test_repr(self):
        """Make sure subclasses have appropriate repr"""
        for x in self.tups:
            self.assertEqual(x, eval(repr(x), {x.__class__.__name__: type(x)}))


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
            def __init__(self, n):
                super(NoIter, self).__init__(n, None)

        class Init(NoInit):
            def __init__(self, n):
                super(Init, self).__init__(n, None)

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
            ForestEnumerator(0)
        with self.assertRaises(ValueError):
            TransformationMonoid(-1)
        with self.assertRaises(ValueError):
            EndofunctionStructures(-1)