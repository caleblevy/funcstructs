"""Metaclass for parametrizing a class by its __init__ parameters.

Caleb Levy, 2015.
"""

import unittest

from inspect import getargspec
from operator import attrgetter

from itertools import chain  # for testing


class ParametrizedMeta(type):
    """Metaclass which parametrizes a class by the parameters of it's __init__
    method. The class is automatically given __slots__ for these parameter
    names. If a class' __init__ is not present or takes no parameters, the
    class is assumed to have no parameters.

    The following restrictions apply to parametrized classes:
        1) They cannot have multiple (direct) bases
        2) All classes in their inheritance chain must have __slots__
        3) Their constructor methods cannot take variable arguments.
    """

    def __new__(mcls, name, bases, dct):
        # Ensure automatically generated attributes are not overloaded
        for attr in ['__slots__', '_get_param_values', '__parameters__',
                     '__setattr__', '__delattr__']:
            if attr in dct:
                raise TypeError(
                    "cannot parametrize %s: overloaded %s" % (name, attr))

        # Imposed for now in the name of general sanity
        if len(bases) > 1:
            raise TypeError("Parametrized classes cannot have multiple bases")
        base = bases[0] if bases else object
        # If any of the bases lack __slots__, so will the derived class
        if '__dict__' in base.__dict__:
            raise TypeError("parametrized class bases must have slots")

        # Extract parameters defined in cls __init__
        if '__init__' not in dct and base.__init__ is object.__init__:
            init_args = getargspec(lambda self: None)
        else:
            init_args = getargspec(dct.get('__init__', base.__init__))
        # Classes must be parametrized with finite number of parameters
        if init_args.varargs is not None or init_args.keywords is not None:
            raise TypeError("variable arguments in %s.__init__" % name)

        current_params = tuple(init_args.args[1:])
        old_params = getattr(base, '__parameters__', frozenset())
        new_params = ()
        for param in current_params:
            if param not in old_params:
                new_params += param,
        pg = attrgetter(*current_params) if current_params else lambda self: ()

        def _get_param_values(self):
            """Return ordered tuple of instance's parameter values"""
            return pg(self)

        # slots must be set before class creation
        dct['__slots__'] = new_params
        dct['__parameters__'] = old_params.union(new_params)
        dct['__'+name+'_parameters__'] = current_params
        dct['_get_param_values'] = _get_param_values

        cls = super(ParametrizedMeta, mcls).__new__(mcls, name, bases, dct)

        if current_params:
            # Design Note: Parametrized objects' behaviors are governed solely
            # by their parameters, thus it is appropriate for ParametrizedABC
            # to make all parameters write-once attributes at class creation.
            #
            # On the other hand, objects with different parameter values may
            # compare mathematically equal, thus client classes are given
            # freedom to implement __eq__ and __hash__.
            def __setattr__(self, attr, val):
                if attr in current_params and hasattr(self, attr):
                    raise AttributeError("Cannot set attribute %r" % attr)
                else:
                    super(cls, self).__setattr__(attr, val)

            def __delattr__(self, attr):
                if attr in current_params and hasattr(self, attr):
                    raise AttributeError("Cannot delete attribute %r" % attr)
                else:
                    super(cls, self).__delattr__(attr)

            cls.__setattr__ = __setattr__
            cls.__delattr__ = __delattr__

        return cls


class ParametrizedMixin(object):
    __metaclass__ = ParametrizedMeta


class ParametrizedMetaValidationTests(unittest.TestCase):
    """Test ParametrizedMeta constructor throws errors on invalid bases"""

    def test_autogenerated_attributes_cannot_be_customized(self):
        """Ensure that setting autogenerated attributes raises runtime error"""
        with self.assertRaises(TypeError):
            class A1(ParametrizedMixin):
                def __setattr__(self, name, val):
                    object.__setattr__(self, name, val)

        with self.assertRaises(TypeError):
            class A2(ParametrizedMixin):
                def __delattr__(self, attr):
                    object.__delattr__(self, attr)

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
        class NoSlots(object):
            pass

        class PhonySlots(object):
            pass

        PhonySlots.__slots__ = ("a", "b", "c", )

        for unslotted in [NoSlots, PhonySlots]:
            with self.assertRaises(TypeError):
                class P(unslotted):
                    __metaclass__ = ParametrizedMeta

    def test_must_have_one_base(self):
        """Test an error is raised when mixing nonparametrized bases"""
        class O1(object):
            __slots__ = ()

        class O2(object):
            __slots__ = ()

        # test inheritance with multiple bases works as expected
        with self.assertRaises(TypeError):
            class P(O1, O2):
                __metaclass__ = ParametrizedMeta

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


class ParametrizedMetaChecks(unittest.TestCase):
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

    def test_attr_setting(self):
        """Test weather attribute creation and deletion is blocked"""
        c2 = self.c2
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
