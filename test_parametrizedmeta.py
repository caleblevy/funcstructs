import unittest

from abc import ABCMeta
from itertools import chain, product

from parametrizedmeta import (
    ParamMeta,
    ParametrizedMixin,
    WriteOnceMixin,
    Struct,
    hascustominit, newclass
)


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
        """Ensure that bases must have slots"""
        Slots = newclass(slots=())
        NoSlots = newclass()
        PhonySlots = newclass()
        PhonySlots.__slots__ = ()

        for bases in [NoSlots, PhonySlots, (Slots, NoSlots)]:
            with self.assertRaises(TypeError):
                newclass(mcls=ParamMeta, bases=bases)

        # test rule 1b
        NonEmptySlots = newclass(slots=("a", "b"))
        FromNonEmpty = newclass(slots=(), bases=NonEmptySlots)
        for bases in [NonEmptySlots, (Slots, NonEmptySlots), FromNonEmpty]:
            with self.assertRaises(TypeError):
                newclass(mcls=ParamMeta, bases=bases)

    def test_rule_2(self):
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
            with self.assertRaises(TypeError) as e:
                newclass(mcls=ParamMeta, bases=bases)

    def test_rule_3(self):
        """Test that only parametrized bases can have __init__"""
        Init = newclass(slots=(), init=lambda self: None)
        NoInit = newclass(slots=())
        Parametrized = newclass(mcls=ParamMeta, init=lambda self: None)
        for bases in ([], [NoInit], [Parametrized], [NoInit, Parametrized]):
            with self.assertRaises(TypeError):
                newclass(mcls=ParamMeta, bases=[Init] + bases)

    def test_rule_4(self):
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

    class A(ParametrizedMixin):
        pass

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

    a = A()
    b = B("11", "22")
    c = C("a")
    c2 = C2("a1", "a2")
    d = D(4, 5, 6)

    paramobjs = [a, b, c, c2, d]

    def test_parameters_attribute(self):
        """Test that ParamMeta keeps track of parameters correctly"""
        self.assertEqual(frozenset(), self.A.__parameters__)
        self.assertEqual({"b1", "b2"}, self.B.__parameters__)
        self.assertEqual({"b1", "b2", "c"}, self.C.__parameters__)
        self.assertEqual({"b1", "b2", "c"}, self.C2.__parameters__)
        self.assertEqual({"b1", "b2", "d"}, self.D.__parameters__)

    def test_init(self):
        """Test parameter values are initialized properly"""
        self.assertEqual(("11", "22"), (self.b.b1, self.b.b2))
        self.assertEqual((1, 2, "a"), (self.c.b1, self.c.b2, self.c.c))
        self.assertEqual(("a1", 2, "a2"), (self.c2.b1, self.c2.b2, self.c2.c))
        self.assertEqual((4, 5, 6), (self.d.b1, self.d.b2, self.d.d))

    def test_slots(self):
        """Test parametrized classes are correctly slotted"""
        for obj in self.paramobjs:
            self.assertTrue(hasattr(obj, '__slots__'))
            self.assertFalse(hasattr(obj, '__dict__'))
            with self.assertRaises(AttributeError):
                setattr(obj, "e", 0)
            # If there are other slotted class in mro, this must be modified
            slots = [getattr(c, '__slots__', ()) for c in type(obj).__mro__]
            # Ensure there are same number of unique slots and parameters
            self.assertEqual(len(obj.__parameters__), sum(map(len, slots)))
            # Ensure that __parameters__ contains all unique slots in mro
            self.assertEqual(obj.__parameters__, set(chain(*slots)))

    def test_param_getter(self):
        """Test paramgetter works correctly"""
        self.assertEqual((), self.a._param_values())
        self.assertEqual(("11", "22"), self.b._param_values())
        self.assertEqual("a", self.c._param_values())
        self.assertEqual(("a1", "a2"), self.c2._param_values())
        self.assertEqual((4, 5, 6), self.d._param_values())


class WriteOnceMixinTests(unittest.TestCase):

    class A(Struct):
        def __init__(self, a, b):
            self.a = a
            self.b = b

    class C(A):
        def __init__(self, a, c):
            super(self.__class__, self).__init__(a, 2)
            self.c = c

    def test_attr_setting(self):
        """Test weather attribute creation and deletion is blocked"""
        c = self.C(1, 3)
        with self.assertRaises(AttributeError):
            c.a = "a"
        with self.assertRaises(AttributeError):
            c.b = "b"
        with self.assertRaises(AttributeError):
            c.c = "c"
        with self.assertRaises(AttributeError):
            del c.a
        with self.assertRaises(AttributeError):
            del c.b
        with self.assertRaises(AttributeError):
            del c.c
        self.assertEqual((1, 2, 3), (c.a, c.b, c.c))


if __name__ == '__main__':
    unittest.main()
