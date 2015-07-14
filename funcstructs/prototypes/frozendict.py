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


_mapping = frozendict._mapping  # store reference to descriptor
del frozendict._mapping  # destroy external access to the mapping
del frozendict.__slots__  # make it look like a builtin type

# Since the member descriptor's "__set__" and "__get__" methods are
# themselves (method) descriptors, a new wrapper for them is generated
# each time they are called. Store references to them locally to avoid
# this step.
_map_set = _mapping.__set__
_map_get = _mapping.__get__


def _frozendict_method(name, map_get):
    """Make wrapper method to access frozendict's internal dict."""
    dict_method = getattr(dict, name)
    if name in {'__getitem__', 'has_key'}:
        def method(self, key):
            return dict_method(map_get(self), key)
    elif name == '__contains__':
        def method(self, item):
            return dict_method(map_get(self), item)
    elif name == 'get':
        def method(self, key, default=None):
            return dict_method(map_get(self), key, default)
    else:
        def method(self):
            return dict_method(map_get(self))
    method.__name__ = name
    method.__doc__ = dict_method.__doc__
    return method


def _FrozendictHelper(fd_cls, map_get=_map_get, map_set=_map_set):
    """Add wrappers for `dict`'s methods to frozendict."""

    def __new__(*args, **kwargs):  # signature allows using `cls` keyword arg
        self = super(fd_cls, args[0]).__new__(args[0])
        # Wrap internal setter inside of __new__
        map_set(self, dict(*args[1:], **kwargs))
        return self
    fd_cls.__new__ = staticmethod(__new__)

    dict_fromkeys = dict.fromkeys  # cache just like for map_get(/set)

    def fromkeys(cls, iterable, v=None):
        """New frozendict with keys from iterable and values set to v."""
        # call cls and copy dict since subclass new might define more
        # conditions (i.e. Multiset)
        return cls(dict_fromkeys(iterable, v))

    fd_cls.fromkeys = classmethod(fromkeys)

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
    # __repr__: since we want to wrap it to add "frozendict" around the
    # dict string, so we can't just return dict.__repr__. We exclude __format__
    # and __str__ since they will depend on __repr__.
    #
    # __setattr__ and __delattr__: since (I believe) those would apply
    # to the internal dict, and just raise AttributeErrors anyway. (TODO:
    # verify this).
    #
    # __eq__ and __ne__: since we must wrap frozendicts to compare equal
    # to both other frozendicts and dicts.
    #
    # Ordering Operations: since (1) in python3 they just
    # raise TypeErrors, which is equally achievable by not giving them
    # comparison operators in the first place, (2) they should probably
    # have done this in python2 anyway, and (3) the presence of these
    # methods annoyingly prevents using functools.total_ordering in case
    # you DO want a subclass which overrides them, while adding no
    # functionality.
    #
    # __reduce__ and __reduce_ex__: because I am not sure how dict
    # pickling works, whether the "frozenness" of the dict should impact it,
    # and how I implement whatever I end up deciding to do.
    # (TODO: rectify this bout of laziness on my part).

    dict_methods = [
        '__contains__',
        '__getitem__',
        '__iter__',
        '__len__',
        'copy',  # no use in returning a new immutable dict, just copy internal
        'get',
        'items',
        'keys',
        'values'
    ]

    # Make frozendict interface resemble dict's as closely as possible.
    # TODO: This may change if it gets annoying.
    if hasattr(dict, 'iterkeys'):
        dict_methods.extend([
            'viewkeys',
            'viewvalues',
            'viewitems',
            'iterkeys',
            'itervalues',
            'iteritems',
            'has_key'
        ])

    if hasattr(dict, '__sizeof__'):  # pypy's dict does not define __sizeof__
        dict_methods.append('__sizeof__')

    for method in dict_methods:
        setattr(fd_cls, method, _frozendict_method(method, map_get))

    def __eq__(self, other):
        # There is technically a way to mutate a frozendict.
        #
        # Hiding the member accessor inside methods works because the
        # "outside world" never directly sees the dict. However,
        # frozendicts are supposed to complement dicts in the same way
        # frozensets complements sets, thus we need to be able to compare a
        # frozendict's internal dictionary against other objects.
        #
        # This potentially exposes the internal dictionary to another type's
        # __eq__ method, which is free to mutate the dict. In particular, we
        # can mutate a frozendict using the following hack:
        #
        # >>> class A(dict):
        # ...   def __eq__(self, other):
        # ...     other[1] = 2
        # ...     return dict.__eq__(self, other)
        # ...
        # >>> a = A()
        # >>> b = frozendict()
        # >>> b == a
        # True
        # >>> b
        # frozendict({1: 2})
        #
        # Note that this hack requires:
        # 1: "A" subclass dict. Types not inheriting from dict will not have
        #    priority over the internal map's dict.__eq__, and thus b == a
        #    would defer to dict.__eq__(map_get(b), a), which will not mutate.
        # 2: the frozendict is on the left-hand side of the comparison.
        #    If we try a == b then A's type will end up trying to mutate b
        #    directly, which raises an error.
        #
        # There are several ways to guard against this, all of which have
        # drawbacks outweighing their (miniscule) benefits:
        #
        # * We could copy the dict at each comparison, and as a further
        #   speed optimization we could do this only for (untrusted) dict
        #   subclasses. This could kill performence in cases sane people might
        #   deal with (i.e. every comparison becomes O(n) no matter what).
        #
        # * We can use a MappingProxyType for the internal map in Python
        #   3.4 or higher (and 2, with ctypes hackery), but this creates
        #   another level of indirection, only works in a documented
        #   fashion in the very latest versions of python, and only on
        #   the CPython implementation.
        #
        # * Finally, we could force frozendict.__eq__ to always take priority,
        #   and call dict.__eq__(map_get(self), other). This will screw
        #   up legitimate behavior on subclasses that (for example)
        #   compare by type.
        #
        # It is my sincere (and naive) hope that anyone smart enough to concoct
        # such a thing would also be smart enough *not to* (again, naive). If
        # your code *accidentally* mutates objects when checking for equality,
        # you have bigger things to worry about.
        #
        # In short, DO NOT define dict subclasses which mutate objects when
        # comparing for equality and your frozendicts will stay frozen.
        if isinstance(other, frozendict):
            return map_get(self) == map_get(other)
        else:
            return map_get(self) == other
    __eq__.__doc__ = dict.__eq__.__doc__
    fd_cls.__eq__ = __eq__

    def __ne__(self, other):
        return not self == other
    __ne__.__doc__ = dict.__ne__.__doc__
    fd_cls.__ne__ = __ne__

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, map_get(self))
    __repr__.__doc__ = dict.__repr__.__doc__
    fd_cls.__repr__ = __repr__

    dict_items = getattr(dict, 'iteritems', dict.items)

    def __hash__(self):
        # default hash independent of overridden items
        return hash(frozenset(dict_items(map_get(self))))
    fd_cls.__hash__ = __hash__


_FrozendictHelper(frozendict)
_Mapping.register(frozendict)


del _Mapping, _frozendict_method, _FrozendictHelper, _mapping
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
