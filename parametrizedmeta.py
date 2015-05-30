"""Metaclass for parametrizing a class by its __init__ parameters.

Caleb Levy, 2015.
"""

import unittest

from inspect import getargspec
from operator import attrgetter


class ParametrizedMeta(type):
    """Metaclass which parametrizes a class by the parameters of it's __init__
    method. If __init__ takes no arguments, the class is assumed to have no
    parameters.

    The arguments to __init__ become write-once attributes, and the class is
    automatically given __slots__, as any parametrized class should be
    immutable."""

    def __new__(mcls, name, bases, dct):
        # extract parameters defined in current cls __init__
        new_params = tuple(getargspec(dct.get('__init__', lambda _: 1))[0][1:])
        # add these parameters to existing slots, if any
        __slots__ = dct.pop('__slots__', ())
        if isinstance(__slots__, str):
            __slots__ = (__slots__, )
        else:
            __slots__ = tuple(__slots__)
        dct['__slots__'] = __slots__ + new_params
        cls = super(ParametrizedMeta, mcls).__new__(mcls, name, bases, dct)
        # acquire parameter names in any bases and add to current parameters
        old_params = ()
        for base in bases:
            old_params += getattr(base, '__parameters__', ())
        params = old_params + new_params
        params_getter = attrgetter(*params) if params else lambda self: ()
        param_names = frozenset(params)

        def _get_param_values(self):
            """Return ordered tuple of instance's parameter values"""
            return params_getter(self)

        def __setattr__(self, attr, val):
            if attr in param_names and hasattr(self, attr):
                raise AttributeError("Cannot set attribute %r" % attr)
            else:
                dct.get('__setattr__', super(cls, self).__setattr__)(attr, val)

        def __delattr__(self, attr):
            if attr in param_names and hasattr(self, attr):
                raise AttributeError("Cannot delete attribute %r" % attr)
            else:
                dct.get('__delattr__', super(cls, self).__delattr__)(attr)

        cls.__parameters__ = params
        cls._get_param_values = _get_param_values
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
            pass

    class C(B):
        def __init__(self, c):
            self.c = 1

    def test_parameters_attribute(self):
        """Test that ParametrizedMeta keeps track of parameters correctly"""
        self.assertEqual((), self.A.__parameters__)
        self.assertEqual(("b1", "b2"), self.B.__parameters__)
        self.assertEqual(("b1", "b2", "c"), self.C.__parameters__)

    def test_slotting(self):
        """Test slots and parameters interact correctly"""
        slotvals = [[], (), "a", ["a"], ("a")]
        inits = [((), lambda self: None), (("b", ), lambda self, b=1: None)]
        # test slots without parameters
        for slots in slotvals:
            for params, init in inits:
                class A(ParametrizedMixin):
                    __slots__ = slots
                    __init__ = init
                a = A()
                self.assertEqual(set(a.__slots__), set(slots).union(params))
                self.assertEqual(set(a.__parameters__), set(params))
                self.assertFalse(hasattr(a, '__dict__'))

    def test_param_getter(self):
        """Test paramgetter works correctly"""
        b = self.B(1, 2)
        with self.assertRaises(AttributeError):
            b._get_param_values()
        b.b1 = "a"
        b.b2 = "b"
        self.assertEqual(("a", "b"), b._get_param_values())

    def test_attr_setting(self):
        """Test weather attribute creation and deletion is blocked"""
        c = self.C(1)
        c.b1 = "a"
        c.b2 = "b"
        with self.assertRaises(AttributeError):
            c.b1 = "a"
        with self.assertRaises(AttributeError):
            c.b2 = "b"
        with self.assertRaises(AttributeError):
            c.c = 1
        with self.assertRaises(AttributeError):
            del c.b1
        with self.assertRaises(AttributeError):
            del c.b2
        with self.assertRaises(AttributeError):
            del c.c
        self.assertEqual(("a", "b", 1), c._get_param_values())

        # Check that slotted attributes are not blocked along with parameters
        class D(ParametrizedMixin):
            __slots__ = "abc"

            def __init__(self, d):
                self.d = d

        d = D(4)
        d.abc = 5
        with self.assertRaises(AttributeError):
            del d.d
        with self.assertRaises(AttributeError):
            d.d = 1
        d.abc = 4
        del d.abc


if __name__ == '__main__':
    unittest.main()
