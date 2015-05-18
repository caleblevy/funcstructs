"""Metaclass for dynamically generating accessors to read-only attributes.

Caleb Levy, 2015.
"""

import abc

from six import with_metaclass


def _popslots(clsdct, attr):
    """Return slots as a tuple of identifiers."""
    slots = clsdct.pop(attr, ())
    if isinstance(slots, str):
        slots = (slots, )
    return tuple(slots)


def ro_parameter(name):
    """Class decorator for adding a property returning self._params[name]. Ex:

    @ro_parameter("name")
    class DecoratedClass(object):
        pass

        :: is equivalent to ::

    class DecoratedClass(object):
        @property
        def name(self):
            return self._params[name]
    """
    def ro_parameter_decorator(cls):
        setattr(cls, name, property(lambda self: self._params[name]))
        return cls
    return ro_parameter_decorator


class ParametrizedABC(abc.ABCMeta):
    """An ABC metaclass accepting a __parameters__ attribute, a listing of
    parameters for which data descriptors will be generated at class
    instantiation. Example usage is as follows (python3 syntax):

    class A(object, metaclass=ParametrizedABC):
        __parameters__ = [n, m]

        :: is equivalent to ::

    class A(object):
        __slots__ = ()

        @property
        def n(self):
            return self._params[n]

        @property
        def m(self):
            return self._params[m]

    The abstractmethod and abstractproperty decorators work for instances of
    ParametrizedABC as expected. All instances of ParametrizedABC are
    automatically slotted."""

    def __new__(mcls, name, bases, dct):
        # process __slots__ and __parameters__ into tuples of identifiers
        slots = _popslots(dct, '__slots__')
        params = _popslots(dct, '__parameters__')
        dct['__slots__'] = slots
        # only add _params to classes not inheriting from an mcls instance
        if not (bases and all(isinstance(base, mcls) for base in bases)):
            dct['__slots__'] += ('_params', )
        cls = super(ParametrizedABC, mcls).__new__(mcls, name, bases, dct)
        # add accessor properties for elements of __parameters__
        for param in params:
            cls = ro_parameter(param)(cls)
        return cls


class Enumerable(with_metaclass(ParametrizedABC, object)):
    """Abstract base class for enumerable objects."""

    def __new__(cls, **kwargs):
        """Return new Enumerable with parameters passed from subclasses"""
        self = super(Enumerable, cls).__new__(cls)
        # add parameters as a frozendict of everything passed to Enumerable
        self._params = kwargs
        return self

    @abc.abstractmethod
    def __iter__(self):
        return
        yield

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
