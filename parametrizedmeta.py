"""Metaclass for parametrizing a class by its __init__ parameters.

Caleb Levy, 2015.
"""

import inspect


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
