from funcstructs.compat import viewitems


class frozendict(dict):
    """Dictionary with no mutating methods. The values themselves, as with
    tuples, may still be mutable. If all of frozendict's values are hashable,
    then so is frozendict."""

    __slots__ = ()

    def __new__(*args, **kwargs):  # signature allows using `cls` keyword arg
        self = dict.__new__(args[0])
        dict.__init__(self, *args[1:], **kwargs)
        return self

    @classmethod
    def fromkeys(*args, **kwargs):
        cls = args[0]
        return cls(dict.fromkeys(*args[1:], **kwargs))

    def __init__(*args, **kwargs):  # signature allows using `self` keyword arg
        pass  # Override dict.__init__ to avoid calling disabled update method

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, dict(self))

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
        return type(self) is type(other) and \
               viewitems(self) == viewitems(other)

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
        return hash(frozenset(self.items())) + id(type(self))

    def split(self):
        """Splits a mapping into corresponding key-value lists."""
        return tuple(self.keys()), tuple(self.values())

    def sort_split(self):
        """Same as frozendict.split with both lists sorted by key values"""
        items = self.items()
        if items:
            return tuple(zip(*sorted(items)))
        else:
            return (), ()


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
