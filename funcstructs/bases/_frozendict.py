# Caleb Levy, 2015.


@classmethod
def _raise_unassignable(cls, *args, **kwargs):
    raise TypeError('%r does not support item assignment' % cls.__name__)


@classmethod
def _raise_undeleteable(cls, *args, **kwargs):
    raise TypeError('%r does not support item deletion' % cls.__name__)


class frozendict(dict):
    """Dictionary with no mutating methods. The values themselves, as with
    tuples, may still be mutable. If all of frozendict's values are hashable,
    then so is frozendict."""

    __slots__ = ()

    def __new__(*args, **kwargs):
        self = dict.__new__(*args, **kwargs)
        dict.__init__(self, *args[1:], **kwargs)
        return self

    @classmethod
    def fromkeys(*args, **kwargs):
        cls = args[0]
        return cls(dict.fromkeys(*args[1:], **kwargs))

    def __init__(*args, **kwargs):
        pass  # Override dict.__init__ to avoid call to self.update()

    # Disable all inherited mutating methods. Based on brownie's ImmutableDict

    __setitem__ = setdefault = update = _raise_unassignable

    __delitem__ = clear = pop = popitem = _raise_undeleteable

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, dict(self))

    def __eq__(self, other):
        if type(self) is type(other):
            return dict.__eq__(self, other)
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
