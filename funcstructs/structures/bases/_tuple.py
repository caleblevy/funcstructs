"""Convenience class for inheriting from tuple.

Caleb Levy, 2015.
"""


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
