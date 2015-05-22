# Caleb Levy, 2015.

import collections

from ._frozendict import frozendict


class Enumerable(collections.Iterable):
    """Convenience class for building combinatorial enumerations"""

    __slots__ = "_params"

    def __new__(cls, **kwargs):
        """Enumerator with behaviour governed by its parameters."""
        self = super(Enumerable, cls).__new__(cls)
        self._params = frozendict(kwargs)
        return self

    def __eq__(self, other):
        """Enumerables are equal iff they have the same type and paremeters"""
        if type(self) is type(other):
            return self._params == other._params
        return False

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(self._params)

    def __repr__(self):
        params = []
        for param, val in self._params.items():
            params.append(param+'='+repr(val))
        return self.__class__.__name__ + '(%s)' % ', '.join(params)

    # block access to _params attribute after creation

    def __setattr__(self, name, val):
        if name == "_params" and hasattr(self, "_params"):
            raise AttributeError("can't set attribute")
        else:
            super(Enumerable, self).__setattr__(name, val)

    def __delattr__(self, name):
        if name == "_params" and hasattr(self, "_params"):
            raise AttributeError("can't delete attribute")
        else:
            super(Enumerable, self).__delattr__(name)


def add_param_getter(cls, name):
    """Add a property with a given name to cls which returns the value assigned
    to name by the _params attribute of cls instances."""
    @property
    def _param_getter(self):
        return self._params[name]
    setattr(cls, name, _param_getter)


def add_new(cls, param_names):
    """Automatically adds __new__ to cls from cls._new if none is defined"""
    # if cls does not have _new, raise error directly at instantiation
    if not hasattr(cls, '_new'):
        # raise runtime error, since this will stop the module from executing
        raise RuntimeError(
            "Cannot parametrize %r without defining _new" % cls.__name__)

    # define our new "__new__"
    @staticmethod
    def __new__(subcls, *args, **kwargs):
        params = subcls._new(*args, **kwargs)
        param_dict = {}
        for name, param in zip(param_names, params):
            param_dict[name] = param
        return super(cls, subcls).__new__(subcls, **param_dict)
    cls.__new__ = __new__    # add __new__ to cls


def parametrize(*params):
    """Add parameters to a class, and set __new__ to automatically parse inputs
    using _new = cls._new.

    Usage:

        @parametrize("a", "b")
        class ParametrizedClass(object):

            @staticmethod
            def _new(a, b):
                return a, b

    Equates to:

        class ParametrizedClass(object):

            @staticmethod
            def _new(a, b):
                return a, b

            def __new__(cls, a, b):
                a, b = cls._new(a, b)
                return super(ParametrizedClass, cls).__new__(cls, a=a, b=b)

            @property
            def a(self):
                return self._params["a"]

            @property
            def b(self):
                return self._params["b"]
    """
    def parametrization_decorator(cls):
        for param in params:
            add_param_getter(cls, param)
        # only add default __new__ if cls does not override Enumerable.__new__
        if cls.__new__ is Enumerable.__new__:
            add_new(cls, params)
        return cls
    return parametrization_decorator
