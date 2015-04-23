"""Abstract base class for enumerable collections of objects parametrized by
integers and partitions.

Caleb Levy, 2015.
"""

import abc
import collections

from . import multiset


class Enumerable(collections.Iterable):

    @abc.abstractmethod
    def __init__(self, n, partition=None):
        self.n = n
        self.partition = multiset.Multiset(partition)

    def __eq__(self, other):
        if type(self) is type(other):
            return self.n == other.n and self.partition == other.partition
        return False

    def __ne__(self, other):
        return not self == other

    def __lt__(self, other):
        return NotImplemented

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
