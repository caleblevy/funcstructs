"""Base classes for implementing endofunction structures.

Caleb Levy, 2015.
"""

import abc
import collections


@classmethod
def _raise_unassignable(cls, *args, **kwargs):
    raise TypeError('%r does not support item assignment' % cls.__name__)


@classmethod
def _raise_undeleteable(cls, *args, **kwargs):
    raise TypeError('%r does not support item deletion' % cls.__name__)


class frozendict(dict):
    """Dictionary with no mutating methods. The values themselves, as with
    tuples, may still be mutable. If all of frozendict's values are hashable,
    then so is frozendict."""

    __slots__ = ()

    def __new__(cls, *args, **kwargs):
        self = super(frozendict, cls).__new__(cls, *args, **kwargs)
        super(frozendict, self).__init__(*args, **kwargs)
        return self

    def __init__(self, *args, **kwargs):
        pass  # Override dict.__init__ to avoid call to self.update()

    # Disable all inherited mutating methods. Based on brownie's ImmutableDict

    __setitem__ = setdefault = update = _raise_unassignable

    __delitem__ = clear = pop = popitem = _raise_undeleteable

    def __hash__(self):
        return hash(frozenset(self.items()))

    def __repr__(self):
        return self.__class__.__name__ + "(%s)" % dict(self)

    def __eq__(self, other):
        if type(self) is type(other):
            return dict.__eq__(self, other)
        return False

    def __ne__(self, other):
        return not self == other

    @classmethod
    def fromkeys(cls, *args, **kwargs):
        return cls(dict.fromkeys(*args, **kwargs))


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
