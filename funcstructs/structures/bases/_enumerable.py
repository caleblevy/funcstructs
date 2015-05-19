# Caleb Levy, 2015.

import abc

from six import with_metaclass

from ._frozendict import frozendict


def _popslots(clsdct, attr):
    """Return slots as a tuple of identifiers."""
    slots = clsdct.pop(attr, ())
    if isinstance(slots, str):
        slots = (slots, )
    return tuple(slots)


def make_param_getter(name):
    """Creates a property returning self._params[name]"""
    @property
    def param_getter(self):
        return self._params[name]
    return param_getter


class ParametrizedABC(abc.ABCMeta):
    """Metaclass for dynamically generating accessors to read-only attributes.

    ParametrizedABC looks for a class's __parameters__ attribute, a list of
    identifier strings defining all relevant class data, and adds data
    descriptors for each parameter at class instantiation. ParametrizedABC's
    are automatically slotted.

    Usage:

        class A(object, metaclass=ParametrizedABC):
            __parameters__ = [n]

    Becomes:

        class A(object):
            __slots__ = ('_params', )
            @property
            def n(self):
                return self._params[n]

    Implementing the _params attribute is left to instances of ParametrizedABC.

    ParametrizedABC inherits from ABCMeta, allowing one to define abstract
    methods and properties as expected."""

    def __new__(mcls, name, bases, dct):
        # process __slots__ and __parameters__ into tuples of identifiers
        slots = _popslots(dct, '__slots__')
        params = _popslots(dct, '__parameters__')
        # add default empty slots
        dct['__slots__'] = slots
        # add accessor properties for elements of __parameters__
        for param_name in params:
            dct[param_name] = make_param_getter(param_name)
        # add _params to classes not inheriting from an mcls instance
        if not (bases and all(isinstance(base, mcls) for base in bases)):
            dct['__slots__'] += ('_params', )
        return super(ParametrizedABC, mcls).__new__(mcls, name, bases, dct)


class Enumerable(with_metaclass(ParametrizedABC, object)):
    """Convenience class for building combinatorial enumerations"""

    @abc.abstractmethod
    def __new__(cls, **kwargs):
        """Enumerator with behaviour governed by its parameters."""
        self = super(Enumerable, cls).__new__(cls)
        self._params = frozendict(kwargs)
        return self

    @abc.abstractmethod
    def __iter__(self):
        return
        yield

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
