"""Parametrized Abstract Base Class for reusable generators.

Caleb Levy, 2015.
"""

from abc import abstractmethod, ABCMeta

from funcstructs.compat import with_metaclass
from funcstructs.bases.parametrized import ParamMeta


class ParametrizedABCMeta(ParamMeta, ABCMeta):
    """Metaclass for creating parametrized abstract base classes."""
    pass


class WriteOnceMixin(object):
    """Mixin class to make all parameters write-once attributes."""
    __slots__ = ()

    def __setattr__(self, name, val):
        if hasattr(self, name):
            raise AttributeError("Cannot set attribute %r" % name)
        super(WriteOnceMixin, self).__setattr__(name, val)

    def __delattr__(self, attr):
        if hasattr(self, attr):
            raise AttributeError("Cannot delete attribute %r" % attr)
        super(WriteOnceMixin, self).__delattr__(attr)


class Struct(with_metaclass(ParamMeta)):
    """Parametrized structure with equality determined by parameter values."""

    def __eq__(self, other):
        if type(self) is type(other):
            return self._param_values() == other._param_values()
        return False

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        param_strings = []
        for name, val in zip(self.__parameters__, self._param_values()):
            param_strings.append('%s=%s' % (name, repr(val)))
        return '%s(%s)' % (self.__class__.__name__, ', '.join(param_strings))

    def __reduce__(self):
        return (self.__class__, self._param_values())


class ImmutableStruct(Struct, WriteOnceMixin):
    """A Struct which becomes immutable once initialized. They are
    hashable, assuming that their parameter values are, and are thus
    suitable for use as dictionary keys."""

    def __hash__(self):
        return hash(self._param_values())


class Enumerable(with_metaclass(ParametrizedABCMeta, ImmutableStruct)):
    """Abstract enumerators for collections of objects parametrized by
    a finite number of variables.
    """
    # TODO: describing differences between this and Sequence, Set, Iterable:
    #   - Should have quick containment testing
    #   - In general is NOT indexable
    #   - Are comparable, immutable, reusable
    #   - In general NOT have fast __len__
    # TODO: add abstract "__contains__"
    # TODO: consider abstract "__len__"

    @abstractmethod
    def __iter__(self):
        return
        yield


def typecheck(*types):
    """Wrap a __contains__ method to check it its input is in types."""
    def wrapping_decorator(contains):
        """Wrapper checking for given types."""
        def __contains__(self, other):
            if isinstance(other, types):
                return contains(self, other)
            else:
                return False
        __contains__.__doc__ = contains.__doc__
        return __contains__
    return wrapping_decorator
