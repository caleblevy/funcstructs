"""Metaclass for parametrizing a class by its __init__ parameters.

Caleb Levy, 2015.
"""

from collections import Iterable
from inspect import getargspec
from operator import attrgetter


def hascustominit(cls):
    """Return true if cls does not call default initializer."""
    # In pypy2, the following:

    # >>>> class A(object): pass
    # >>>> A.__init__ is object.__init__

    # returns False. Hence the need to traverse class dicts in mro
    for c in type.mro(cls):  # works with type
        if '__init__' in c.__dict__:
            return c is not object


class ParamMeta(type):
    """Metaclass which parametrizes a class by the parameters of it's __init__
    method. The class is automatically given __slots__ for these parameter
    names. If a class' __init__ is not present or takes no parameters, the
    class is assumed to have none.

    The following restrictions apply to parametrized classes:
    1) All (non-parametrized) bases in their mro must have (empty) __slots__
    2) There can only be one in a class's bases
    3) If one has a base with a constructor, that base must be parametrized
    4) Their constructor methods cannot take variable arguments.

    Additionally, the '__parameters__' and '__slots__' attributes of
    parametrized classes are reserved for internal use.
    """

    def __new__(mcls, name, bases, dct):
        # Rule 0: No Reserved Names
        # -------------------------
        for attr in ['__slots__', '__parameters__']:
            if attr in dct:
                raise TypeError("cannot set reserved attribute %r" % attr)

        have_slots = ['__dict__' not in base.__dict__ for base in bases]
        are_parametrized = [isinstance(base, ParamMeta) for base in bases]
        define_init = [hascustominit(base) for base in bases]

        # Rule 1: All Bases Have Slots
        # ----------------------------
        # If any of the bases lack __slots__, so will the derived class.
        # Parametrized classes are meant to be "simple", akin to namedtuples,
        # thus the only attributes they accept are their parameters.
        for base, has_slots in zip(bases, have_slots):
            if not has_slots:
                raise TypeError("base %s does not have __slots__" % base)
        # Rule 1b: Unparametrized Bases Have Empty __slots__
        # --------------------------------------------------
        # All significant attributes of a parametrized class should be declared
        # and set in its __init__ method. If a member descripter is not set in
        # a parametrized base, it is not useful. If it is set in two locations
        # in the mro, the behaviour is technically undefined (see notes on
        # slots at https://docs.python.org/3/reference/datamodel.html).
        for base, is_parametrized in zip(bases, are_parametrized):
            if not is_parametrized:
                if any(getattr(b, '__slots__', False) for b in base.__mro__):
                    raise TypeError("unparametrized base with nonempty slots")

        # Rule 2: Max of One Parametrized Base
        # ------------------------------------
        # A parametrized class defines an object "parametrized" by a fixed
        # set of "variables". In this model, __init__ declares the parameters
        # and the rest of the class describes the system governed by those
        # inputs.
        #
        # Since all parametrized classes have __slots__, inheriting from two
        # of them requires both have identical slot structure. Conceptually
        # these correspond to different systems governed by the same
        # parameters.
        #
        # Multiple inheritance makes most sense when the bases describe
        # *independent* aspects of an object's nature. The requirement of slots
        # only allows mixing different interpretations of the *same*
        # parameters. It thus makes no sense to have multiple parametrized
        # bases.
        param_base = None
        if any(are_parametrized):
            if are_parametrized.count(True) > 1:
                raise TypeError("multiple parametrized bases")
            param_base = bases[are_parametrized.index(True)]

        # Rule 3: No Unparametrized Initializers
        # --------------------------------------
        # Parametrization is meant to begin at the first parametrized class
        # in the inheritance chain; any other mix-in classes should serve only
        # to add *behavior* to the system.
        def default_init(): pass  # getargspec(object.__init__) raises error
        for has_init, is_parametrized in zip(define_init, are_parametrized):
            if has_init:
                if not is_parametrized:
                    raise TypeError("multiple __init__'s in bases")
                default_init = param_base.__init__

        # Rule 4: Fixed Parameter Count
        # -----------------------------
        # Parametrized classes are supposed to represent *specific* systems
        # governed by a small, very straightforward set of parameters. It
        # makes no sense to allow variable arguments in this context.
        init_args = getargspec(dct.get('__init__', default_init))
        if init_args.varargs is not None or init_args.keywords is not None:
            raise TypeError("variable arguments in %s.__init__" % name)

        current_params = tuple(init_args.args[1:])
        old_params = getattr(param_base, '__parameters__', frozenset())
        new_params = ()
        for param in current_params:
            if param not in old_params:
                new_params += param,

        # slots must be set before class creation
        dct['__slots__'] = new_params
        dct['__parameters__'] = old_params.union(new_params)

        # convenience
        pg = attrgetter(*current_params) if current_params else lambda self: ()
        dct.setdefault('_get_param_values', lambda self: pg(self))
        dct.setdefault('__'+name+'_parameters__', current_params)

        return super(ParamMeta, mcls).__new__(mcls, name, bases, dct)


def newclass(mcls=type, name="newclass", bases=(), **special):
    """Return blank class with the given metaclass, __slots__, __init__
    function and bases. Additional keyword arguments added to class dict."""
    if not isinstance(bases, Iterable):
        bases = (bases, )
    bases = tuple(bases)
    dct = {}
    for attr, val in special.items():
        if val is not None:
            dct['__'+attr+'__'] = val
    return mcls(name, bases, dct)


ParametrizedMixin = newclass(mcls=ParamMeta, name="ParametrizedMixin")


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


class ParameterStruct(ParametrizedMixin, WriteOnceMixin):
    """Parametrized structure with equality and comparison determined by the
    parameters"""
    pass
