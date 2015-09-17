"""Frozen dictionary using a proxy pattern.

Caleb Levy, 2015.
"""

from collections import Mapping as _Mapping
from functools import partial as _partial
from types import FunctionType as _FunctionType

__all__ = ["frozendict"]

# frozendict is essentially a pure-python implementation of a
# MappingProxyType (python3) or DictProxyType (python2).
#
# First we create skeleton class with a single slot to hold a mapping
# internally. We then remove the slot's member descriptor from the class
# dict, and retain a private reference to it inside the _map_accessors
# function via a closure.
#
# _FrozendictHelper creates wrappers for the builtin dict's non-mutating
# methods which access frozendict's internal mapping using the private
# descriptor. Since all access is guarded by these non-mutating methods,
# there is no public mechanism to alter the internal dict.
#
# The proxy pattern provides a nice bemefit: all methods (with the
# exception of __ne__, which is the negation of __eq__) are guaranteed to
# be totally independent; i.e. we can override any combination of
# methods, and the remaining ones will be unaffected. This holds true
# regardless of any implicit relationships between the builtin dict's
# methods, giving consistent behavior across implementations.
#
# The main drawback is the convoluted code; since frozendict reflects
# MappingProxyType in design, its code ends up looking similar to
# CPython: define a type struct referencing another object and bolt on
# methods for it.


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
@_partial
def _map_accessors(_map_set=frozendict._mapping.__set__,
                   _map_get=frozendict._mapping.__get__):
    return _map_set, _map_get


# Define all methods inside _FrozendictHelper so that all references to the
# helper functions are internal to the function body, and not module level
# exports. This also wraps map_get and map_set inside closure cells so that
# altering them at the module level does not change method behavior.
#
# Can't make this a decorator like _MultisetHelper since we need _map_get and
# _map_set to already be defined prior to calling.
@_FunctionType.__call__
def _FrozendictHelper():
    """Add wrappers for `dict`'s methods to frozendict."""
    del frozendict._mapping  # destroy external access to the mapping
    del frozendict.__slots__  # make it look like a builtin type

    map_set, map_get = _map_accessors()

    @staticmethod
    def __new__(*args, **kwargs):  # signature allows using `cls` keyword arg
        self = object.__new__(args[0])
        # Wrap internal setter inside of __new__
        map_set(self, dict(*args[1:], **kwargs))
        return self
    frozendict.__new__ = __new__

    @classmethod
    def fromkeys(cls, iterable, v=None):
        """New frozendict with keys from iterable and values set to v."""
        # call cls and copy dict since subclass new might define more
        # conditions (i.e. Multiset)
        return cls(dict.fromkeys(iterable, v))
    frozendict.fromkeys = fromkeys

    def add_with_docs(func):
        name = func.__name__
        if func.__doc__ is None:
            func.__doc__ = getattr(dict, name).__doc__
        setattr(frozendict, name, func)

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
    # Ordering Operations: since (1) in python3 they just raise
    # TypeErrors, which is equally achievable by not giving them
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

    @add_with_docs
    def __reduce__(self):
        return (self.__class__, (map_get(self), ))

    @add_with_docs
    def get(self, key, default=None):
        return map_get(self).get(key, default)

    @add_with_docs
    def copy(self):
        return map_get(self).copy()

    @add_with_docs
    def items(self):
        return map_get(self).items()

    @add_with_docs
    def keys(self):
        return map_get(self).keys()

    @add_with_docs
    def values(self):
        return map_get(self).values()

    # Add (view,iter)keys/values/items methods back to
    # python2/pypy2/jython implementations of frozendict; the bare
    # items/values/keys methods now return lists in these versions.
    #
    # This change was originally kicked off due to a bug in Jython's
    # keyword argument unpacking. When calling dict(**frozendict()),
    # Jython first calls frozendict.keys(). It expects a list here, and
    # it relies on the fact that lists are indexable. When
    # frozendict.keys() returned a dict_keys view object, it raised a
    # TypeError instead.
    #
    # Although this particular problem an implementation detail of
    # Jython, there is a deeper issue. frozendict is to dict as set is to
    # frozenset: in every situation that does not involve hashing or
    # mutation, they are totally interchangeable. This means that, until
    # the user performs one of those two actions, they should neither
    # need to know nor care whether the dict at hand is frozen or not.
    #
    # Sadly, this schizm in behavior is PART OF THE DICT INTERFACE
    # ITSELF. When the user calls six.viewitems(frozendict()), they
    # expect a view on its items, not a TypeError, both in Python2 and
    # Python3. It should satisfy the collections.Mapping ABC contract in
    # both versions. To do this requires adding back the headache
    # inducing methods.
    #
    # As a compromise, frozendict provides _(items/keys/values) methods
    # which return views in both 2 and 3.

    frozendict._items = frozendict.items
    frozendict._keys = frozendict.keys
    frozendict._values = frozendict.values

    @add_with_docs
    def __hash__(self):
        # default hash independent of overridden items
        return hash(frozenset(map_get(self).items()))

    if hasattr(dict, 'itervalues'):
        @add_with_docs
        def viewitems(self):
            return map_get(self).viewitems()

        @add_with_docs
        def viewkeys(self):
            return map_get(self).viewkeys()

        @add_with_docs
        def viewvalues(self):
            return map_get(self).viewvalues()

        @add_with_docs
        def iteritems(self):
            return map_get(self).iteritems()

        @add_with_docs
        def iterkeys(self):
            return map_get(self).iterkeys()

        @add_with_docs
        def itervalues(self):
            return map_get(self).itervalues()

        # Make hash use the lazy version of items in both versions.

        @add_with_docs
        def __hash__(self):
            return hash(frozenset(map_get(self).viewitems()))

        # Calling frozendict.method in python2 returns an "unbound method type"
        # instead of a function, so access class __dict__ directly.

        frozendict._items = frozendict.__dict__['viewitems']
        frozendict._keys = frozendict.__dict__['viewkeys']
        frozendict._values = frozendict.__dict__['viewvalues']

    if hasattr(dict, '__sizeof__'):  # pypy's dict does not define __sizeof__
        @add_with_docs
        def __sizeof__(self):
            return map_get(self).__sizeof__()

    _Mapping.register(frozendict)
