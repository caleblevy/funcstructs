"""Metaclass for parametrizing a class by its __init__ parameters.

Caleb Levy, 2015.
"""


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
    pass
