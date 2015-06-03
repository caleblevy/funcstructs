"""Metaclass for parametrizing a class by its __init__ parameters.

Caleb Levy, 2015.
"""

import unittest

from inspect import getargspec
from operator import attrgetter

# imports for testing
from abc import ABCMeta
from collections import Iterable
from itertools import chain, product


def hascustominit(cls):
    """Return true if cls does not call default initializer."""
    # In pypy2, the following:

    # >>>> class A(object): pass
    # >>>> A.__init__ is object.__init__

    # returns False. Hence the need to traverse class dicts in mro
    for c in type.mro(cls):  # works with type
        if '__init__' in c.__dict__:
            return c is not object


class ParametrizedMeta(type):
    """Metaclass which parametrizes a class by the parameters of it's __init__
    method. The class is automatically given __slots__ for these parameter
    names. If a class' __init__ is not present or takes no parameters, the
    class is assumed to have none.

    The following restrictions apply to parametrized classes:
    1) All (non-parametrized) bases in their mro must have (empty) __slots__
    2) There can only be one in a class's bases
    3) If one has a base with a constructor, that base must be parametrized
    4) Their constructor methods cannot take variable arguments.

    Additionally, the '__parameters__' and '__slots__' attributes of
    parametrized classes are reserved for internal use.
    """

    def __new__(mcls, name, bases, dct):
        # Rule 0: No Reserved Names
        # -------------------------
        for attr in ['__slots__', '__parameters__']:
            if attr in dct:
                raise TypeError("cannot set reserved attribute %r" % attr)

        have_slots = ['__dict__' not in b.__dict__ for b in bases]
        are_parametrized = [isinstance(b, ParametrizedMeta) for b in bases]
        define_init = [hascustominit(b) for b in bases]

        # Rule 1: All Bases Have Slots
        # ----------------------------
        # If any of the bases lack __slots__, so will the derived class.
        # Parametrized classes are meant to be "simple", akin to namedtuples,
        # thus the only attributes they accept are their parameters.
        for base, has_slots in zip(bases, have_slots):
            if not has_slots:
                raise TypeError("base %s does not have __slots__" % base)
        # Rule 1b: Unparametrized Bases Have Empty __slots__
        # --------------------------------------------------
        # All significant attributes of a parametrized class should be declared
        # and set in its __init__ method. If a member descripter is not set in
        # a parametrized base, it is not useful. If it is set in two locations
        # in the mro, the behaviour is technically undefined (see notes on
        # slots at https://docs.python.org/3/reference/datamodel.html).
        for base, is_parametrized in zip(bases, are_parametrized):
            if not is_parametrized:
                if any(getattr(b, '__slots__', False) for b in base.__mro__):
                    raise TypeError("unparametrized base with nonempty slots")

        # Rule 2: Max of One Parametrized Base
        # ------------------------------------
        # A parametrized class defines an object "parametrized" by a fixed
        # set of "variables". In this model, __init__ declares the parameters
        # and the rest of the class describes the system governed by those
        # inputs.
        #
        # Since all parametrized classes have __slots__, inheriting from two
        # of them requires both have identical slot structure. Conceptually
        # these correspond to different systems governed by the same
        # parameters.
        #
        # Multiple inheritance makes most sense when the bases describe
        # *independent* aspects of an object's nature. The requirement of slots
        # only allows mixing different interpretations of the *same*
        # parameters. It thus makes no sense to have multiple parametrized
        # bases.
        param_base = None
        if any(are_parametrized):
            if are_parametrized.count(True) > 1:
                raise TypeError("multiple parametrized bases")
            param_base = bases[are_parametrized.index(True)]

        # Rule 3: No Unparametrized Initializers
        # --------------------------------------
        # Parametrization is meant to begin at the first parametrized class
        # in the inheritance chain; any other mix-in classes should serve only
        # to add *behavior* to the system.
        def default_init(): pass  # getargspec(object.__init__) raises error
        for has_init, is_parametrized in zip(define_init, are_parametrized):
            if has_init:
                if not is_parametrized:
                    raise TypeError("multiple __init__'s in bases")
                default_init = param_base.__init__

        # Rule 4: Fixed Parameter Count
        # -----------------------------
        # Parametrized classes are supposed to represent *specific* systems
        # governed by a small, very straightforward set of parameters. It
        # makes no sense to allow variable arguments in this context.
        init_args = getargspec(dct.get('__init__', default_init))
        if init_args.varargs is not None or init_args.keywords is not None:
            raise TypeError("variable arguments in %s.__init__" % name)

        current_params = tuple(init_args.args[1:])
        old_params = getattr(param_base, '__parameters__', frozenset())
        new_params = ()
        for param in current_params:
            if param not in old_params:
                new_params += param,

        # slots must be set before class creation
        dct['__slots__'] = new_params
        dct['__parameters__'] = old_params.union(new_params)

        # convenience
        pg = attrgetter(*current_params) if current_params else lambda self: ()
        dct.setdefault('_get_param_values', lambda self: pg(self))
        dct.setdefault('__'+name+'_parameters__', current_params)

        return super(ParametrizedMeta, mcls).__new__(mcls, name, bases, dct)


def newclass(mcls=type, name="newclass", bases=(), **special):
    """Return blank class with the given metaclass, __slots__, __init__
    function and bases. Additional keyword arguments added to class dict."""
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


ParametrizedMixin = newclass(mcls=ParametrizedMeta, name="ParametrizedMixin")
ParametrizedABCMeta = newclass(
    bases=ABCMeta, name="ParametrizedABCMeta", new=ParametrizedMeta.__new__
)


class ParametrizedInheritanceRulesTests(unittest.TestCase):
    """Test ParametrizedMeta constructor throws errors on invalid bases"""

    def test_rule_0(self):
        """Ensure reserved attributes are unsettable"""
        reserved = ['slots', 'parameters']
        for word in reserved:
            with self.assertRaises(TypeError):
                newclass(mcls=ParametrizedMeta, **{word: ()})

    def test_rule_1(self):
        """Ensure that bases must have slots"""
        Slots = newclass(slots=())
        NoSlots = newclass()
        PhonySlots = newclass()
        PhonySlots.__slots__ = ()

        for bases in [NoSlots, PhonySlots, (Slots, NoSlots)]:
            with self.assertRaises(TypeError):
                newclass(mcls=ParametrizedMeta, bases=bases)

        # test rule 1b
        NonEmptySlots = newclass(slots=("a", "b"))
        FromNonEmpty = newclass(slots=(), bases=NonEmptySlots)
        for bases in [NonEmptySlots, (Slots, NonEmptySlots), FromNonEmpty]:
            with self.assertRaises(TypeError):
                newclass(mcls=ParametrizedMeta, bases=bases)

    def test_rule_2(self):
        """Test that a class cannot derive from multiple parametrized bases"""
        T1 = newclass(slots=())
        T2 = newclass(slots=())
        T3 = newclass(slots=())
        T12 = newclass(slots=(), bases=[T1, T2])
        # Check that we can mix and match inheritance in various ways
        P1 = newclass(mcls=ParametrizedMeta, bases=T12, init=lambda self: 0)
        P2 = newclass(mcls=ParametrizedMeta, bases=[P1, T2])
        P3 = newclass(mcls=ParametrizedMeta, bases=P1)
        for bases in [(P1, P2), (P1, P3), (P1, P3, T3)]:
            with self.assertRaises(TypeError) as e:
                newclass(mcls=ParametrizedMeta, bases=bases)

    def test_rule_3(self):
        """Test that only parametrized bases can have __init__"""
        Init = newclass(slots=(), init=lambda self: None)
        NoInit = newclass(slots=())
        Parametrized = newclass(mcls=ParametrizedMeta, init=lambda self: None)
        for bases in ([], [NoInit], [Parametrized], [NoInit, Parametrized]):
            with self.assertRaises(TypeError):
                newclass(mcls=ParametrizedMeta, bases=[Init] + bases)

    def test_rule_4(self):
        """Test that __init__ methods cannot have variable arguments"""
        inits = [
            (lambda *a: None), (lambda **k: None), (lambda *a, **k: None),
            (lambda _, *a: None), (lambda _, **k: None),
            (lambda _, *a, **k: None)
        ]
        for init in inits:
            for bases in [newclass(slots=()), newclass(mcls=ParametrizedMeta)]:
                with self.assertRaises(TypeError):
                    newclass(init=init, bases=bases, mcls=ParametrizedMeta)


class ParametrizedMetaTests(unittest.TestCase):
    """Verify the properties of ParametrizedMeta instances"""

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
        """Test that ParametrizedMeta keeps track of parameters correctly"""
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
        self.assertEqual((), self.a._get_param_values())
        self.assertEqual(("11", "22"), self.b._get_param_values())
        self.assertEqual("a", self.c._get_param_values())
        self.assertEqual(("a1", "a2"), self.c2._get_param_values())
        self.assertEqual((4, 5, 6), self.d._get_param_values())


class WriteOnceMixin(object):
    """Mixin class to make all parameters write-once attributes."""
    __slots__ = ()

    def __setattr__(self, name, val):
        if hasattr(self, name):
            raise AttributeError("Cannot set attribute %r" % name)
        super(WriteOnceMixin, self).__setattr__(name, val)

    def __delattr__(self, attr):
        if hasattr(self, attr):
            raise AttributeError("Cannot delete attribute %r" % attr)
        super(WriteOnceMixin, self).__delattr__(attr)


class ParameterStruct(ParametrizedMixin, WriteOnceMixin):
    """Parametrized structure with equality and comparison determined by the
    parameters"""
    pass


class WriteOnceMixinTests(unittest.TestCase):

    class A(ParameterStruct):
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
