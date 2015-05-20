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

    def __new__(cls, *args, **kwargs):
        self = super(frozendict, cls).__new__(cls, *args, **kwargs)
        super(frozendict, self).__init__(*args, **kwargs)
        return self

    def __init__(self, *args, **kwargs):
        pass  # Override dict.__init__ to avoid call to self.update()

    # Disable all inherited mutating methods. Based on brownie's ImmutableDict

    __setitem__ = setdefault = update = _raise_unassignable

    __delitem__ = clear = pop = popitem = _raise_undeleteable

    def __hash__(self):
        return hash(frozenset(self.items()))

    def __repr__(self):
        return self.__class__.__name__ + "(%s)" % dict(self)

    def __eq__(self, other):
        if type(self) is type(other):
            return dict.__eq__(self, other)
        return False

    def __ne__(self, other):
        return not self == other

    @classmethod
    def fromkeys(cls, *args, **kwargs):
        return cls(dict.fromkeys(*args, **kwargs))
