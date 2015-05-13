"""Convenience class for building combinatorial enumerations.

Caleb Levy, 2015.
"""

import abc
import collections

from .. import multiset


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
