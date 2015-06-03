"""Metaclass for parametrizing a class by its __init__ parameters.

Caleb Levy, 2015.
"""

import unittest

from inspect import getargspec
from operator import attrgetter

from itertools import chain  # for testing

from six import with_metaclass


def hascustominit(cls):
    """Return true if cls does not call default initializer"""
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
    class is assumed to have no parameters.

    The following restrictions apply to parametrized classes:
    1) Their (non-parametrized) bases must have (empty) __slots__
    2) There can only be one in a class' bases
    3) If one has a base with a constructor, that base must be parametrized
    4) Their constructor methods cannot take variable arguments.

    Additionally, the '__parameters__' and '__slots__' attributes of
    parametrized classes are reserved for internal use.
    """

    def __new__(mcls, name, bases, dct):
        # Rule 0) No Reserved Names
        for attr in ['__slots__', '_get_param_values', '__parameters__']:
            if attr in dct:
                raise TypeError("cannot set reserved attribute %r" % attr)

        have_slots = ['__dict__' not in b.__dict__ for b in bases]
        are_parametrized = [isinstance(b, ParametrizedMeta) for b in bases]
        define_init = [hascustominit(b) for b in bases]

        # Rule 1) All Bases Have Slots
        # ----------------------------
        # If any of the bases lack __slots__, so will the derived class.
        # Parametrized classes are meant to be "simple", akin to namedtuples,
        # thus the only attributes they accept are their parameters.
        for base, has_slots in zip(bases, have_slots):
            if not has_slots:
                raise TypeError("base %s does not have __slots__" % base)
        # Rule 1b) Unparametrized Bases Have Empty __slots__
        # --------------------------------------------------
        # Since parametrized class cannot have initializers, it makes no sense
        # for them to define their own __slots__.
        for base, is_parametrized in zip(bases, are_parametrized):
            if getattr(base, '__slots__', False) and not is_parametrized:
                raise TypeError("unparametrized base with nonempty slots")

        # Rule 2) Max of One Parametrized Base
        # ------------------------------------
        # A parametrized class defines an object "parametrized" by a fixed
        # set of "variables". In this model, __init__ declares the parameters
        # and the rest of the class describes the system governed by those
        # inputs.
        #
        # Since all parametrized classes have __slots__, inheriting from two
        # of them requires both have identical slot structure. Conceptually
        # these corresponds to different systems governed by the same
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

        # Rule 3) No Unparametrized Initializers
        # --------------------------------------
        # Parametrization is meant to begin at the first parametrized class
        # in the inheritance chain to be parametrized; any other mix-in
        # classes should serve only to add behavior to the system.
        def default_init(): pass  # getargspec(object.__init__) raises error
        for has_init, is_parametrized in zip(define_init, are_parametrized):
            if has_init:
                if not is_parametrized:
                    raise TypeError("multiple __init__'s in bases")
                default_init = param_base.__init__

        # Rule 4) Fixed Parameter Count
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


class ParametrizedMixin(with_metaclass(ParametrizedMeta, object)):

    # Make all parameters write-once attributes

    def __setattr__(self, name, val):
        if name in self.__parameters__ and hasattr(self, name):
            raise AttributeError("Cannot set attribute %r" % name)
        else:
            super(ParametrizedMixin, self).__setattr__(name, val)

    def __delattr__(self, attr):
        if attr in self.__parameters__ and hasattr(self, attr):
            raise AttributeError("Cannot delete attribute %r" % attr)
        else:
            super(ParametrizedMixin, self).__delattr__(attr)


class ParametrizedMetaValidationTests(unittest.TestCase):
    """Test ParametrizedMeta constructor throws errors on invalid bases"""

    def test_autogenerated_attributes_cannot_be_customized(self):
        """Ensure that setting autogenerated attributes raises runtime error"""
        with self.assertRaises(TypeError):
            class A3(ParametrizedMixin):
                __slots__ = ()

        with self.assertRaises(TypeError):
            class A4(ParametrizedMixin):
                __parameters__ = ("a", "b", "c")

        with self.assertRaises(TypeError):
            class A5(ParametrizedMixin):
                def _get_param_values(self):
                    return ()

    def test_bases_must_have_slots(self):
        """Test that TypeError is raised if instances of bases have dicts"""
        class Slotted(object):
            __slots__ = ()

        class Unslotted(object):
            pass

        class PhonySlots(object):
            pass

        PhonySlots.__slots__ = ("a", "b", "c", )

        # Can inherit from slotted base
        class A(with_metaclass(ParametrizedMeta, Slotted)):
            pass

        for bases in [(Unslotted, ), (PhonySlots, ), (Slotted, Unslotted)]:
            with self.assertRaises(TypeError):
                class P(with_metaclass(ParametrizedMeta, *bases)):
                    pass

    def test_bases_cannot_have_multiple_inits(self):
        """Test an error is raised when parametrizing from multiple bases"""
        class B1(object):
            __slots__ = ()

        class B2(object):
            __slots__ = ()

        class B3(object):
            __slots__ = ()

            def __init__(self):
                pass

        class P1(with_metaclass(ParametrizedMeta)):
            pass

        class P2(with_metaclass(ParametrizedMeta)):
            pass

        class B23(B2, B3):
            __slots__ = ()

        for bases in [(B1, B2), (B1, P1), (B1, B2, P1)]:
            class P(with_metaclass(ParametrizedMeta, *bases)):
                pass

        for bases in [(B3, ), (B1, B3), (B23, ), (P1, P2)]:
            with self.assertRaises(TypeError):
                class P(with_metaclass(ParametrizedMeta, *bases)):
                    pass

    def test_constructor_cannot_have_variable_parameters(self):
        """Ensure that presence of *args/**kwargs in __init__ raises error."""
        with self.assertRaises(TypeError):
            class B1(ParametrizedMixin):
                def __init__(*args):
                    self, args = args

        with self.assertRaises(TypeError):
            class B2(ParametrizedMixin):
                def __init__(self, a, *ar):
                    self.a = a

        with self.assertRaises(TypeError):
            class B3(ParametrizedMixin):
                def __init__(self, a, b, **kw):
                    self.a = a
                    self.b = b


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


class ParametrizedMixinTests(unittest.TestCase):

    def test_attr_setting(self):
        """Test weather attribute creation and deletion is blocked"""
        c2 = ParametrizedMetaTests.c2
        with self.assertRaises(AttributeError):
            c2.b1 = "a"
        with self.assertRaises(AttributeError):
            c2.b2 = "b"
        with self.assertRaises(AttributeError):
            c2.c = 1
        with self.assertRaises(AttributeError):
            del c2.b1
        with self.assertRaises(AttributeError):
            del c2.b2
        with self.assertRaises(AttributeError):
            del c2.c
        self.assertEqual(("a1", 2, "a2"), (c2.b1, c2.b2, c2.c))


if __name__ == '__main__':
    unittest.main()
