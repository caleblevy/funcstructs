"""Metaclass for parametrizing a class by its __init__ parameters.

Caleb Levy, 2015.
"""

import inspect
import unittest


def add_hash(cls, params):
    def __hash__(self):
        pass
    cls.__hash__ = __hash__


def add_repr(cls, params):
    def __repr__(self):
        pass
    cls.__repr__ = __repr__


def add_eq(cls, params):
    def __eq__(self, other):
        pass
    cls.__eq__ = __eq__


def add_setattr(cls, params):
    def __setattr__(self, name, val):
        pass
    cls.__setattr__ = __setattr__


def add_delattr(cls, params):
    def __delattr__(self, name):
        pass
    cls.__delattr__ = __delattr__


class ParametrizedMeta(type):
    """Metaclass which parametrizes a class by the parameters of it's __init__
    method. If __init__ takes no arguments, the class is assumed to have no
    parameters.

    The arguments to __init__ become write-once attributes, and the class is
    automatically given __slots__, as any parametrized class should be
    immutable."""

    def __new__(mcls, name, bases, dct):
        # extract parameters defined in current cls
        init = dct.get('__init__', None)
        if init is not None:
            new_params = tuple(inspect.getargspec(init)[0][1:])
        else:
            new_params = ()
        # add these parameters to existing slots, if any
        slots = dct.pop('__slots__', ())
        if isinstance(slots, str):
            slots = (slots, )
        dct['__slots__'] = tuple(slots) + new_params
        # acquire parameter names in any bases and add to current parameters
        old_params = ()
        for base in bases:
            old_params += getattr(base, '__parameters__', ())
        dct['__parameters__'] = old_params + new_params  # preserve order
        return super(ParametrizedMeta, mcls).__new__(mcls, name, bases, dct)


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


if __name__ == '__main__':
    unittest.main()
