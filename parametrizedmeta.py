"""Metaclass for parametrizing a class by its __init__ parameters.

Caleb Levy, 2015.
"""

import unittest

from inspect import getargspec
from operator import attrgetter


class ParametrizedMeta(type):
    """Metaclass which parametrizes a class by the parameters of it's __init__
    method. If a class' __init__ is not present or takes no parameters, the
    class is assumed to have no parameters.

    The arguments to __init__ become write-once attributes, and the class is
    automatically given __slots__. A parametrized class should be treated as
    immutable.

    Usage:

        class ParametrizedClass(object, metaclass=ParametrizedMeta):
            def __init__(self, a, b):
                self.a = a
                self.b = b
    """

    def __new__(mcls, name, bases, dct):
        # Ensure automatically generated attributes are not overloaded
        for attr in ['__slots__', '_get_param_values', '__parameters__',
                     '__setattr__', '__delattr__']:
            if attr in dct:
                raise RuntimeError("Cannot parametrize class %s with "
                                   "overloaded %s" % (name, attr))

        # Explicitly check for ParametrizedMeta. Let the python runtime bring
        # any metaclass subclassing conflicts to the user's attention direclty.
        are_parametrized = [isinstance(b, ParametrizedMeta) for b in bases]
        if any(are_parametrized):
            if not all(are_parametrized):
                # Mixing a parametrized class with a non-parametrized slotted
                # class with will fail due to instance layout conflict.
                # Meanwhile, a base without __slots__ makes any derived class
                # unslotted,  which would ruin the point of parametrization.
                #
                # It thus makes no sense to mix parametrized and unparametrized
                # classes.
                raise TypeError("metaclass conflict: mixing parametrized and "
                                "non-parametrized bases")

        # Extract parameters defined in cls __init__
        init_args = getargspec(dct.get('__init__', lambda self: None))
        # Classes must be parametrized with finite number of parameters
        varmsg = "Cannot parametrize class %s with %s in __init__"
        if init_args.varargs is not None:
            raise RuntimeError(varmsg % (name, 'variable args'))
        if init_args.keywords is not None:
            raise RuntimeError(varmsg % (name, "variable keywords"))

        params = tuple(init_args.args[1:])
        # slots must be set before class creation
        dct['__slots__'] = params

        cls = super(ParametrizedMeta, mcls).__new__(mcls, name, bases, dct)

        params_getter = attrgetter(*params) if params else lambda self: ()

        def _get_param_values(self):
            """Return ordered tuple of instance's parameter values"""
            return params_getter(self)

        cls.__parameters__ = params
        cls._get_param_values = _get_param_values

        if params:
            # Design Note: Parametrized objects' behaviors are governed solely
            # by their parameters, thus it is appropriate for ParametrizedABC
            # to make all parameters write-once attributes at class creation.
            #
            # On the other hand, objects with different parameter values may
            # compare mathematically equal, thus client classes are given
            # freedom to implement __eq__ and __hash__.
            param_names = frozenset(params)

            def __setattr__(self, attr, val):
                if attr in param_names and hasattr(self, attr):
                    raise AttributeError("Cannot set attribute %r" % attr)
                else:
                    super(cls, self).__setattr__(attr, val)

            def __delattr__(self, attr):
                if attr in param_names and hasattr(self, attr):
                    raise AttributeError("Cannot delete attribute %r" % attr)
                else:
                    super(cls, self).__delattr__(attr)

            cls.__setattr__ = __setattr__
            cls.__delattr__ = __delattr__

        return cls


class ParametrizedMixin(object):
    __metaclass__ = ParametrizedMeta


class ParametrizedMetaTests(unittest.TestCase):

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
        self.assertEqual((), self.A.__parameters__)
        self.assertEqual(("b1", "b2"), self.B.__parameters__)
        self.assertEqual(("c", ), self.C.__parameters__)
        self.assertEqual(("b1", "c"), self.C2.__parameters__)
        self.assertEqual(("b1", "b2", "d"), self.D.__parameters__)

    def test_init(self):
        """Test parameter values are initialized properly"""
        self.assertEqual(("11", "22"), (self.b.b1, self.b.b2))
        self.assertEqual((1, 2, "a"), (self.c.b1, self.c.b2, self.c.c))
        self.assertEqual(("a1", 2, "a2"), (self.c2.b1, self.c2.b2, self.c2.c))
        self.assertEqual((4, 5, 6), (self.d.b1, self.d.b2, self.d.d))

    def test_slotting(self):
        """Test slots and parameters interact correctly"""
        # Note: find way to test and eliminate duplicate slots
        for obj in self.paramobjs:
            self.assertEqual(obj.__parameters__, obj.__slots__)
            self.assertFalse(hasattr(obj, '__dict__'))
            with self.assertRaises(AttributeError):
                setattr(obj, "e", 0)
            self.assertFalse(hasattr(obj, "e"))

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

    def test_cannot_mix_parametrized_and_unparametrized_bases(self):
        """Test an error is raised when mixing nonparametrized bases"""
        class ObjectMixin(object):
            pass

        with self.assertRaises(TypeError):
            class ObjectParam(ParametrizedMixin, ObjectMixin):
                pass

    def test_autogenerated_attributes_cannot_be_customized(self):
        """Ensure that setting autogenerated attributes raises runtime error"""
        with self.assertRaises(RuntimeError):
            class A1(ParametrizedMixin):
                def __setattr__(self, name, val):
                    object.__setattr__(self, name, val)

        with self.assertRaises(RuntimeError):
            class A2(ParametrizedMixin):
                def __delattr__(self, attr):
                    object.__delattr__(self, attr)

        with self.assertRaises(RuntimeError):
            class A3(ParametrizedMixin):
                __slots__ = ()

        with self.assertRaises(RuntimeError):
            class A4(ParametrizedMixin):
                __parameters__ = ("a", "b", "c")

        with self.assertRaises(RuntimeError):
            class A5(ParametrizedMixin):
                def _get_param_values(self):
                    return ()

    def test_class_cannot_have_variable_number_of_parameters(self):
        """Ensure that presence of *args/**kwargs in __init__ raises error."""
        with self.assertRaises(RuntimeError):
            class B1(ParametrizedMixin):
                def __init__(*args):
                    self, args = args

        with self.assertRaises(RuntimeError):
            class B2(ParametrizedMixin):
                def __init__(self, a, *ar):
                    self.a = a

        with self.assertRaises(RuntimeError):
            class B3(ParametrizedMixin):
                def __init__(self, a, b, **kw):
                    self.a = a
                    self.b = b


if __name__ == '__main__':
    unittest.main()
