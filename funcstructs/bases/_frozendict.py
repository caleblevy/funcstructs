from collections import Mapping

from funcstructs.compat import viewitems


class frozendict(dict):
    """Dictionary with no mutating methods. The values themselves, as with
    tuples, may still be mutable. If all of frozendict's values are hashable,
    then so is frozendict."""

    __slots__ = ()

    # One small disadvantage to Werkzeug's ImmutableDict: technically you can
    # mutate it using __init__; not the case here.

    def __new__(*args, **kwargs):  # signature allows using `cls` keyword arg
        self = dict.__new__(args[0])
        dict.__init__(self, *args[1:], **kwargs)
        return self

    def __init__(*args, **kwargs):  # signature allows using `self` keyword arg
        pass  # Override dict.__init__ to avoid calling disabled update method

    @classmethod
    def fromkeys(cls, iterable, v=None):
        """New frozendict with keys from iterable, and values set to v."""
        return cls(dict.fromkeys(iterable, v))

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, dict(self))

    __str__ = __repr__  # needed for Jython

    def __eq__(self, other):
        # Instances of frozendict subclasses must have same items AND
        # type to compare equal. This supports their diverse use cases as
        # rooted trees, conjugacy classes, functions and Multisets. Even
        # if all *could* have the same items, they are very different
        # data structures.
        #
        # Calling viewitems explicitly allows Jython compatibility
        # without ugly conditional method definitions, and doing so does
        # not seem to induce a significant speed hit.
        if isinstance(other, Mapping):
            return viewitems(self) == viewitems(other)
        return False

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        # A bug in jython 2.7.0 causes it to ignore custom __eq__ methods
        # of dict subclasses with __hash__ upon hash collision. As a
        # temprorary fix, mix in the id of self's type. As long as this
        # does not exceed hash width, the offsets should ensure different
        # frozendict subclasses comparing equal have different hashes.
        #
        # Alternatively we could have a registry of dict subclasses to
        # guarentee no collisions, but I don't want to use such hacks to
        # deal with broken behavior in jython.
        return hash(frozenset(self.items()))


# Disable all mutating methods. Sadly, we must inherit from dict since in
# python 3.4 we cannot inherit from MappingProxy to add __hash__, and pypy and
# Jython don't even have a MappingProxy implementation
_assignment_ops = ['__setitem__', 'setdefault', 'update']
_deletion_ops = ['__delitem__', 'clear', 'pop', 'popitem']


def _disabled_op(name, op):
    """Disable a method performing a given mutating operation."""
    def disabledfunc(cls, *args, **kwargs):
        raise TypeError("%s does not support %s" % (cls.__name__, op))
    disabledfunc.__name__ = name
    disabledfunc.__doc__ = "Disabled method %s" % name
    return classmethod(disabledfunc)


for op in _assignment_ops:
    setattr(frozendict, op, _disabled_op(op, "item assignment"))
for op in _deletion_ops:
    setattr(frozendict, op, _disabled_op(op, "item deletion"))
