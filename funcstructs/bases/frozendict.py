"""Frozen dictionary using a proxy pattern.

Caleb Levy, 2015.
"""

from collections import Mapping as _Mapping

__all__ = ["frozendict"]

# frozendict is essentially a pure-python implementation of a
# MappingProxyType (python3) or DictProxyType (python2).
#
# First we create frozendict with a single slot to hold a mapping
# internally. We then remove the slot's member descriptor from the class
# dict, and retain a private reference to it in the module body.
#
# _FrozendictHelper creates wrappers for the builtin dict's
# non-mutating methods which acces frozendict's internal mapping using
# the private descriptor. Since all access is "guarded" by these
# non-mutating methods, there is no public mechanism to alter the
# internal dict. (*) frozendict is thus truly immutable.
#
# Using a proxy pattern provides a nice benefit: all methods (with the
# exception of __ne__, which is the negation of __eq__) are guaranteed to
# be totally independent; i.e. we can override any combination of
# methods, and the remaining ones will be unaffected. This holds true
# regardless of any implicit relationships between the builtin dict's
# methods, giving consistent cross-platform behavior.
#
# The main drawback is the convoluted code; since frozendict reflects
# MappingProxyType in design, its code ends up looking similar to CPython:
# define a type struct referencing another object and bolt on methods for it.
#
# (*) Under certain circumstances, it may mutate. See comments in __eq__.


class frozendict(object):
    """Dictionary with no mutating methods. The values themselves, as
    with tuples, may still be mutable. If all of frozendict's values
    are hashable, then so is frozendict."""

    __slots__ = '_mapping'  # allocate slot for iternal dict


# Store accessor and setter for the member descriptor.
#
# Since the member descriptor's "__set__" and "__get__" methods are
# themselves (method) descriptors, a new wrapper for them is generated
# each time they are called. Store references to them locally to avoid
# this step.
_map_set = frozendict._mapping.__set__
_map_get = frozendict._mapping.__get__

del frozendict._mapping  # destroy external access to the mapping
del frozendict.__slots__  # make it look like a builtin type


# Define all methods inside _FrozendictHelper so that all references to the
# helper functions are internal to the function body, and not module level
# exports. This also wraps map_get and map_set inside closure cells so that
# altering them at the module level does not change method behavior.
#
# Can't make this a decorator like _MultisetHelper since we need _map_get and
# _map_set to already be defined prior to calling.
def _FrozendictHelper(fd_cls, map_get=_map_get, map_set=_map_set):
    """Add wrappers for `dict`'s methods to frozendict."""

    def __new__(*args, **kwargs):  # signature allows using `cls` keyword arg
        self = object.__new__(args[0])
        # Wrap internal setter inside of __new__
        map_set(self, dict(*args[1:], **kwargs))
        return self
    fd_cls.__new__ = staticmethod(__new__)

    def fromkeys(cls, iterable, v=None):
        """New frozendict with keys from iterable and values set to v."""
        # call cls and copy dict since subclass new might define more
        # conditions (i.e. Multiset)
        return cls(dict.fromkeys(iterable, v))
    fd_cls.fromkeys = classmethod(fromkeys)

    def add_with_docs(func):
        name = func.__name__
        if func.__doc__ is None:
            func.__doc__ = getattr(dict, name).__doc__
        setattr(fd_cls, name, func)

    # All of dict's non-mutating methods, EXCEPT:
    #
    # __del__: since (hopefully) the gc will be unaware that there is
    # a slot without a member descriptor; it should just see a C struct and
    # delete each field. When it sees the internal dict is one of those, it
    # then deletes the dict. (TODO: test the above on different
    # implementations, putting garbage collector benchmarks in the tests.)
    #
    # __init__: since frozendict is not a dict, and the internal dict
    # is already initialized inside __new__.
    #
    # __setattr__ and __delattr__: since (I believe) those would apply
    # to the internal dict, and just raise AttributeErrors anyway. (TODO:
    # verify this).
    #
    # Ordering Operations: since (1) in python3 they just
    # raise TypeErrors, which is equally achievable by not giving them
    # comparison operators in the first place, (2) they should probably
    # have done this in python2 anyway, and (3) the presence of these
    # methods annoyingly prevents using functools.total_ordering in case
    # you DO want a subclass which overrides them, while adding no
    # functionality.
    #
    # The "iter" and "view" versions of "values", "keys" and "items"
    # methods. The only reason to add these in would be making a python2
    # frozendict looks like a python2 dict. Since this distinction causes
    # numerous headaches (for myself), and I am so far the only user, I
    # am pleasing no one by artificially maintaining them.
    #
    # has_key: This method is so old that even invoking it raises a pep8
    # warning. Adding it in would be arcane.
    #
    # __reduce__ and __reduce_ex__: because I am not sure how dict
    # pickling works, whether the "frozenness" of the dict should impact it,
    # and how I implement whatever I end up deciding to do.
    # (TODO: rectify this bout of laziness on my part).

    @add_with_docs
    def __contains__(self, key):
        return key in map_get(self)

    @add_with_docs
    def __getitem__(self, key):
        return map_get(self)[key]

    @add_with_docs
    def __iter__(self):
        return iter(map_get(self))

    @add_with_docs
    def __len__(self):
        return len(map_get(self))

    @add_with_docs
    def get(self, key, default=None):
        return map_get(self).get(key, default)

    @add_with_docs
    def copy(self):
        return map_get(self).copy()

    # Make two distinct function definitions for speed; we want it to compile
    # to bytecode which explicitly calls the method in question.
    if hasattr(dict, 'itervalues'):
        @add_with_docs
        def items(self):
            """D.items() -> a set-like object providing a view on D's items"""
            return map_get(self).viewitems()

        @add_with_docs
        def keys(self):
            """D.keys() -> a set-like object providing a view on D's keys"""
            return map_get(self).viewkeys()

        @add_with_docs
        def values(self):
            """D.values() -> an object providing a view on D's values"""
            return map_get(self).viewvalues()

        @add_with_docs
        def __hash__(self):
            # default hash independent of overridden items
            return hash(frozenset(map_get(self).viewitems()))

        @add_with_docs
        def iteritems(self):
            return map_get(self).iteritems()

    else:
        @add_with_docs
        def items(self):
            return map_get(self).items()

        @add_with_docs
        def keys(self):
            return map_get(self).keys()

        @add_with_docs
        def values(self):
            return map_get(self).values()

        @add_with_docs
        def __hash__(self):
            return hash(frozenset(map_get(self).items()))

    if hasattr(dict, '__sizeof__'):  # pypy's dict does not define __sizeof__
        @add_with_docs
        def __sizeof__(self):
            return map_get(self).__sizeof__()

    @add_with_docs
    def __eq__(self, other):
        if isinstance(other, frozendict):
            other = map_get(other)
        return map_get(self).__eq__(other)

    @add_with_docs
    def __ne__(self, other):
        return not self == other

    @add_with_docs
    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, repr(map_get(self)))


_FrozendictHelper(frozendict)
_Mapping.register(frozendict)


del _Mapping, _FrozendictHelper
# Leave _map_set and _map_get for frozendict subclasses (Multiset).


# TODO: Investigate the following:
# 1) Should I add internal _hash cache?
# 2) Are there any MI issues I am not aware of? (Jython, inheriting from base)
# 3) dict(frozendict_subclass) with different __iter__, __copy__, etc...
# 4) Interaction of (3) with registering frozendict as Mapping
# 5) Performance on different implementations
# 6) Inheriting slots with same name?
# 7) Figure out how to shut pylint up about missing methods (because oh God
#    there will be so many...).
