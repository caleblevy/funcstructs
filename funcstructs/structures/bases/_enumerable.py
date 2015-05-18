# Caleb Levy, 2015.

import abc
import collections

from ._frozendict import frozendict


class Enumerable(collections.Iterable):
    """Convenience class for building combinatorial enumerations"""

    @abc.abstractmethod
    def __new__(cls, **kwargs):
        """Enumerator with behaviour governed by its parameters."""
        self = super(Enumerable, cls).__new__(cls)
        self._params = frozendict(kwargs)
        return self

    def __init__(self, *args, **kwargs):
        # Autoinit for speed
        for param, value in self._params.items():
            setattr(self, param, value)

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
