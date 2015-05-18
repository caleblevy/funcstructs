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
        self.__params = frozendict(kwargs)
        return self

    def __init__(self, *args, **kwargs):
        # Autoinit for speed
        for param, value in self.__params.items():
            setattr(self, param, value)

    def __eq__(self, other):
        """Enumerables are equal iff they have the same type and paremeters"""
        if type(self) is type(other):
            return self.__params == other.__params
        return False

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(self.__params)

    def __repr__(self):
        params = []
        for param, val in self.__params.items():
            params.append(param+'='+repr(val))
        return self.__class__.__name__ + '(%s)' % ', '.join(params)
