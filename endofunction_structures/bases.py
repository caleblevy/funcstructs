"""Base classes for implementing endofunction structures.

Caleb Levy, 2015.
"""

import abc
import collections

from . import multiset


class Tuple(tuple):
    """Base class for hashable finite immutable sequences."""

    __slots__ = ()

    def __repr__(self):
        return self.__class__.__name__+'(%s)' % list(self)

    def __eq__(self, other):
        """Tuples are equal iff they are of the same type and content"""
        if type(self) is type(other):
            return tuple.__eq__(self, other)
        return False

    def __ne__(self, other):
        return not self == other

    # Override arithmetic methods

    def __add__(self, other):
        return NotImplemented

    __mul__ = __rmul__ = __add__

    def __radd__(self, other):
        # tuple.__add__ can handle members of derived classes. This will allow
        # subclasses to override their parents __add__, but not vice-versa. See
        # "How to determine which instance of an operator is being called?" at
        # http://stackoverflow.com/a/18261625/3349520.
        if issubclass(type(self), type(other)):
            raise TypeError("Unsupported operand type(s) for *: %s and %s" % (
                repr(other.__class__.__name__), repr(self.__class__.__name__)))
        return NotImplemented

    __hash__ = tuple.__hash__  # required in python3 when __eq__ is overloaded


class Enumerable(collections.Iterable):
    """Abstract base class for enumerable collections of objects parametrized
    by integers and partitions"""

    @abc.abstractmethod
    def __init__(self, n, partition, lower_bound=-float('inf')):
        """Enumerator parametrized by an integer greater than lower_bound and
        multiset of objects."""
        if n is not None and n < lower_bound:
            raise ValueError(
                "Cannot define %r on %s nodes" % (self.__class__.__name__, n))
        self.__n = n
        self.__partition = multiset.Multiset(partition)

    @property
    def n(self):
        """Integer parameter, if any."""
        return self.__n

    @property
    def partition(self):
        """Multiset parameter, if any."""
        return self.__partition

    def __eq__(self, other):
        """Enumerables are equal iff they have the same type and paremeters"""
        if type(self) is type(other):
            return self.n == other.n and self.partition == other.partition
        return False

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash((self.n, self.partition))

    def __repr__(self):
        enumstr = self.__class__.__name__ + '('
        if self.n is not None:
            enumstr += str(self.n)
            if self.partition:
                enumstr += ', '
        if self.partition:
            enumstr += repr(list(self.partition))
        return enumstr + ')'
