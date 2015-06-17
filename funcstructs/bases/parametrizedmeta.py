"""Metaclass for parametrizing a class by its __init__ parameters.

Caleb Levy, 2015.
"""

from abc import abstractmethod, ABCMeta
from inspect import getargspec
from operator import attrgetter

from funcstructs.compat import with_metaclass


def hascustominit(cls):
    """Return true if cls does not call default initializer."""
    # In pypy2, the following:

    # >>>> class A(object): pass
    # >>>> A.__init__ is object.__init__

    # returns False. Hence the need to traverse class dicts in mro
    for c in type.mro(cls):
        if '__init__' in c.__dict__:
            return c is not object


def base_slots(cls):
    """Return all member descriptors in C and its bases."""
    slots = set()
    for c in type.mro(cls):
        slots.update(getattr(c, '__slots__', ()))
    return slots


class ParamMeta(type):
    """A parametrized type.

    Parametrized classes represent objects whose behavior is determined by a
    fixed set of independent variables. They are automatically assigned
    __slots__ and accessors for the parameters of their __init__ methods.

    Parametrized types enforce the following contract:
    --------------------------------------------------
    1) All of their bases define __slots__.
    2) Their unparametrized bases do not override the default __init__. Mixin
       classes can define behavior, but not the fundamental variables.
    3) The __slots__ of their unparametrized bases are empty.
    4) They cannot be multiply inherited from.
    5) Their __init__ methods cannot take variable arguments.

    Additionally, the '__parameters__' and '__slots__' attributes of
    parametrized classes are reserved for internal use.
    """

    def __new__(mcls, name, bases, dct):
        slotted = ['__dict__' not in base.__dict__ for base in bases]
        parametrized = [isinstance(base, ParamMeta) for base in bases]
        initialized = [hascustominit(base) for base in bases]

        # Extract __init__ parameters
        def default_init(self): pass
        if any(parametrized):
            param_base = bases[parametrized.index(True)]
            if hascustominit(param_base):
                default_init = param_base.__init__
        init_args = getargspec(dct.get('__init__', default_init))

        # Enforce the Contract
        # --------------------

        # RULE 0) No Reserved Names.
        for attr in ['__slots__', '__parameters__']:
            if attr in dct:
                raise TypeError("cannot set reserved attribute %r" % attr)
        # RULE 1) All Bases Have Slots. This requirement guarantees
        # access to __dict__ is prevented for objects of the resulting
        # type. See "notes on using slots" in the documentation of
        # Python's data model.
        for base, has_slots in zip(bases, slotted):
            if not has_slots:
                raise TypeError("base %s does not have __slots__" % base)
        # RULE 2) No Unparametrized __init__.
        for has_init, is_parametrized in zip(initialized, parametrized):
            if has_init and not is_parametrized:
                raise TypeError("unparametrized base with __init__")
        # RULE 3) Unparametrized Bases Have Slots. This is a natural
        # consequence of maintaining consistancy between the __slots__
        # and parameters of the type's bases, along with imposing rules
        # one and two.
        for base, is_parametrized in zip(bases, parametrized):
            if not is_parametrized and base_slots(base):
                raise TypeError("unparametrized base with nonempty slots")
        # RULE 4) Max of One Parametrized Base. Instance layout conflicts
        # prevent mixing of types with different parameters, and the meaning
        # of inheriting from different bases with the same parameters is
        # unclear, leaving little reason to allow it.
        if parametrized.count(True) > 1:
            raise TypeError("multiple parametrized bases")
        # RULE 5) Fixed Parameter Count.
        if init_args.varargs is not None or init_args.keywords is not None:
            raise TypeError("variable arguments in %s.__init__" % name)

        # Add __slots__ to new type. This must be done before class creation,
        # which is why we need a metaclass. Take care not to duplicate names of
        # existing member descriptors, which could lead to undefined behavior,
        # as per the python docs.
        current_params = tuple(init_args.args[1:])
        old_params = set()
        for base in bases:
            old_params.update(base_slots(base))
        new_params = ()
        for param in current_params:
            if param not in old_params:
                new_params += param,
        dct['__slots__'] = new_params

        # For docs and convenience
        dct['__parameters__'] = current_params
        # Make sure _param_values always returns a tuple
        if not current_params:
            def _param_values(self): return ()
        else:
            pg = attrgetter(*current_params)
            if len(current_params) == 1:
                def _param_values(self): return pg(self),
            else:
                def _param_values(self): return pg(self)
        dct.setdefault('_param_values', _param_values)
        return super(ParamMeta, mcls).__new__(mcls, name, bases, dct)


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


class ImmutableStruct(Struct, WriteOnceMixin):
    """A Struct which becomes immutable once initialized. They are hashable,
    assuming that their parameter values are, and are thus suitable for use as
    dictionary keys."""

    def __hash__(self):
        return hash(self._param_values())


class Enumerable(with_metaclass(ParametrizedABCMeta, ImmutableStruct)):
    """Abstract enumerators for collections of objects parametrized by a finite
    number of variables."""

    @abstractmethod
    def __iter__(self):
        return
        yield
