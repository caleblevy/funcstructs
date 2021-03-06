import unittest

from abc import ABCMeta
from collections import Iterable
from itertools import chain, product

from funcstructs.bases.parametrized import (
    hascustominit,
    ParamMeta,
)


def newclass(mcls=type, name="newclass", bases=(), **special):
    """Return a new class with the given metaclass, name and bases. Additional
    keyword arguments are added as class attributes wrapped in double
    underscores.

    Usage:
        A = newclass()
        B = newclass(name="B", init=lambda self: None)
        C = newclass(ABCMeta, "C", [A, B], doc="A new abstract class C")
    """
    if not isinstance(bases, Iterable):
        bases = (bases, )
    bases = tuple(bases)
    dct = {}
    for attr, val in special.items():
        if val is not None:
            dct['__'+attr+'__'] = val
    return mcls(name, bases, dct)


class ClassmakerTests(unittest.TestCase):

    def test_newclass(self):
        class A(object):
            __slots__ = ()

        class B(object):
            __slots__ = ()

        slotsets = [None, (), "abc", ("a", "b"), ["a", "b", "c"]]
        inits = [None, (lambda self: None), (lambda self, *args: None)]
        basesets = [(), object, [object], [A, B]]
        metaclasses = [type, ABCMeta]
        for s, i, b, m in product(slotsets, inits, basesets, metaclasses):
            C = newclass(slots=s, init=i, bases=b, mcls=m)
            # test __slots__
            if s is not None:
                self.assertEqual(s, C.__slots__)
                self.assertNotIn('__dict__', C.__dict__)
            else:
                self.assertNotIn('__slots__', C.__dict__)
                self.assertIn('__dict__', C.__dict__)
            # test __init__
            if i is None:
                self.assertFalse(hascustominit(C))
            else:
                self.assertEqual(i, C.__dict__['__init__'])
            # test bases
            if not b or b is object:
                b = object,
            self.assertEqual(tuple(b), C.__bases__)
            # test metaclass
            self.assertEqual(m, type(C))


class ParametrizedInheritanceRulesTests(unittest.TestCase):
    """Test ParamMeta constructor throws errors on invalid bases"""

    def test_rule_0(self):
        """Ensure reserved attributes are unsettable"""
        reserved = ['slots', 'parameters']
        for word in reserved:
            with self.assertRaises(TypeError):
                newclass(mcls=ParamMeta, **{word: ()})

    def test_rule_1(self):
        """Ensure that bases must have __slots__"""
        Slots = newclass(slots=())
        NoSlots = newclass()
        PhonySlots = newclass()
        PhonySlots.__slots__ = ()
        for bases in [NoSlots, PhonySlots, (Slots, NoSlots)]:
            with self.assertRaises(TypeError):
                newclass(mcls=ParamMeta, bases=bases)

    def test_rule_2(self):
        """Test that only parametrized bases can have __init__"""
        Init = newclass(slots=(), init=lambda self: None)
        NoInit = newclass(slots=())
        Parametrized = newclass(mcls=ParamMeta, init=lambda self: None)
        for bases in ([], [NoInit], [Parametrized], [NoInit, Parametrized]):
            with self.assertRaises(TypeError):
                newclass(mcls=ParamMeta, bases=[Init] + bases)

    def test_rule_3(self):
        """Test that unparametrized bases must have empty __slots__"""
        Slots = newclass(slots=())
        NonEmptySlots = newclass(slots=("a", "b"))
        FromNonEmpty = newclass(slots=(), bases=NonEmptySlots)
        for bases in [NonEmptySlots, (Slots, NonEmptySlots), FromNonEmpty]:
            with self.assertRaises(TypeError):
                newclass(mcls=ParamMeta, bases=bases)

    def test_rule_4(self):
        """Test that a class cannot derive from multiple parametrized bases"""
        T1 = newclass(slots=())
        T2 = newclass(slots=())
        T3 = newclass(slots=())
        T12 = newclass(slots=(), bases=[T1, T2])
        # Check that we can mix and match inheritance in various ways
        P1 = newclass(mcls=ParamMeta, bases=T12, init=lambda self: 0)
        P2 = newclass(mcls=ParamMeta, bases=[P1, T2])
        P3 = newclass(mcls=ParamMeta, bases=P1)
        for bases in [(P1, P2), (P1, P3), (P1, P3, T3)]:
            with self.assertRaises(TypeError):
                newclass(mcls=ParamMeta, bases=bases)

    def test_rule_5(self):
        """Test that __init__ methods cannot have variable arguments"""
        inits = [
            (lambda *a: None), (lambda **k: None), (lambda *a, **k: None),
            (lambda _, *a: None), (lambda _, **k: None),
            (lambda _, *a, **k: None)
        ]
        for init in inits:
            for bases in [newclass(slots=()), newclass(mcls=ParamMeta)]:
                with self.assertRaises(TypeError):
                    newclass(init=init, bases=bases, mcls=ParamMeta)


class ParamMetaTests(unittest.TestCase):
    """Verify the properties of ParamMeta instances"""

    A = newclass(ParamMeta)

    class B(A):
        def __init__(self, b1, b2):
            self.b1 = b1
            self.b2 = b2

    class C(B):
        def __init__(self, c):
            super(self.__class__, self).__init__(1, 2)
            self.c = c

    class C2(B):
        def __init__(self, b1, c):
            super(self.__class__, self).__init__(b1, 2)
            self.c = c

    class D(B):
        def __init__(self, b1, b2, d):
            super(self.__class__, self).__init__(b1, b2)
            self.d = d

    class E(D):
        def __init__(self, b1, f, e):
            self.b2 = self.d = 0
            self.b1 = b1
            self.e = e
            self.f = f

    a = A()
    b = B("11", "22")
    c = C("a")
    c2 = C2("a1", "a2")
    d = D(4, 5, 6)
    e = E(-3, -1, -2)

    paramobjs = [a, b, c, c2, d, e]

    def test_parameters_attribute(self):
        """Test that __parameters__ attribute reflects __init__ parameters"""
        self.assertEqual((), self.A.__parameters__)
        self.assertEqual(("b1", "b2"), self.B.__parameters__)
        self.assertEqual(("c", ), self.C.__parameters__)
        self.assertEqual(("b1", "c"), self.C2.__parameters__)
        self.assertEqual(("b1", "b2", "d"), self.D.__parameters__)
        self.assertEqual(("b1", "f", "e"), self.E.__parameters__)

    def test_init(self):
        """Test parameter values are initialized properly"""
        self.assertEqual(("11", "22"), (self.b.b1, self.b.b2))
        self.assertEqual((1, 2, "a"), (self.c.b1, self.c.b2, self.c.c))
        self.assertEqual(("a1", 2, "a2"), (self.c2.b1, self.c2.b2, self.c2.c))
        self.assertEqual((4, 5, 6), (self.d.b1, self.d.b2, self.d.d))
        self.assertEqual(
            (-3, 0, 0, -2, -1),
            (self.e.b1, self.e.b2, self.e.d, self.e.e, self.e.f)
        )

    def test_slots(self):
        """Test parametrized classes are correctly slotted"""
        for obj in self.paramobjs:
            self.assertTrue(hasattr(obj, '__slots__'))
            self.assertFalse(hasattr(obj, '__dict__'))
            with self.assertRaises(AttributeError):
                setattr(obj, "g", 0)
        for P in map(type, self.paramobjs):
            slots = [getattr(c, '__slots__', ()) for c in P.__mro__]
            # Ensure there are same number of unique slots and total
            self.assertEqual(len(set(chain(*slots))), sum(map(len, slots)))

    def test_param_getter(self):
        """Test paramgetter works correctly"""
        self.assertEqual((), self.a._param_values())
        self.assertEqual(("11", "22"), self.b._param_values())
        self.assertEqual(("a", ), self.c._param_values())
        self.assertEqual(("a1", "a2"), self.c2._param_values())
        self.assertEqual((4, 5, 6), self.d._param_values())
