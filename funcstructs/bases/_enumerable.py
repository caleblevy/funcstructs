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


def parametrize(*params):
    """Add parameters to a class.

    Usage:

        @parametrize('a', 'b')
        class A(object):
            pass

    Equates to:

        class A(object):
            @property
            def a(self):
                return self._params['a']

            @property
            def b(self):
                return self._params['b']
    """
    def parametrization_decorator(cls):
        for param in params:
            add_param_getter(cls, param)
        return cls
    return parametrization_decorator
