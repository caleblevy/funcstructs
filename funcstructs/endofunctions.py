"""Data structures for representing endofunctions: mappings from a finite set
into itself.

Caleb Levy, 2015.
"""

import itertools
import random

from . import bases, productrange

__all__ = [
    "cached_property",
    "Endofunction", "SymmetricFunction",
    "randfunc", "randperm", "randconj",
    "TransformationMonoid"
]


# Modification of werkzeug.cached_property. Here we have chosen not to
# implement a setter for stronger interface guarantees that the properties will
# not change.
class cached_property(property):

    """A decorator that converts a function into a lazy property.  The
    function wrapped is called the first time to retrieve the result
    and then that calculated result is used the next time you access
    the value::
        class Foo(object):
            @cached_property
            def foo(self):
                # calculate something important here
                return 42
    The class has to have a `__dict__` in order for this property to
    work.
    """

    # implementation detail: A subclass of python's builtin property
    # decorator, we override __get__ to check for a cached value. If one
    # choses to invoke __get__ by hand the property will still work as
    # expected because the lookup logic is replicated in __get__ for
    # manual invocation.

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        if self.fget.__name__ not in obj.__dict__:
            obj.__dict__[self.fget.__name__] = self.fget(obj)
        return obj.__dict__[self.fget.__name__]


class Endofunction(bases.Tuple):
    """Implementation of an endofunction as a map of range(N) into itself using
    a list."""

    @classmethod
    def from_tree(cls, tree):
        """Make an endofunction representing a tree."""
        return cls(tree._labelling())

    def __str__(self):
        funcstring = self.__class__.__name__+'(['
        mapvals = []
        for x, f in enumerate(self[:-1]):
            mapvals.append(str(x)+'->'+str(f)+', ')
        funcstring += ''.join(mapvals)
        funcstring += str(len(self)-1)+"->"+str(self[-1])+'])'
        return funcstring

    def __mul__(self, other):
        """(f * g)[x] <==> f[g[x]]"""
        # f * g becomes a function on g's domain, so it inherits class of g
        return other.__class__(self[x] for x in other)

    @cached_property
    def domain(self):
        """The set of objects for which f[x] is defined"""
        return frozenset(range(len(self)))

    @cached_property
    def image(self):
        """f.image <==> {f[x] for x in f.domain}"""
        return frozenset(self)

    @cached_property
    def preimage(self):
        """f.preimage[y] <==> {x for x in f.domain if f[x] == y}"""
        preim = [set() for _ in range(len(self))]
        for x in self.domain:
            preim[self[x]].add(x)
        return tuple(map(frozenset, preim))

    @cached_property
    def imagepath(self):
        """f.imagepath[n] <==> len((f**n).image)"""
        cardinalities = [len(self.image)]
        f = self
        card_prev = len(self)
        for it in range(1, len(self)-1):
            f *= self
            card = len(f.image)
            cardinalities.append(card)
            # Save some time; if we have reached the fixed set, return.
            if card == card_prev:
                cardinalities.extend([card]*(len(self)-2-it))
                break
            card_prev = card
        return tuple(cardinalities)

    def __pow__(self, n):
        """f**n <==> the nth iterate of f"""
        # Convert to string of binary digits, clip off 0b, then reverse.
        component_iterates = bin(n)[2::][::-1]
        f = self
        f_iter = self.__class__(range(len(self)))
        # Iterate by self-composing, akin to exponentiation by squaring.
        for it in component_iterates:
            if it == '1':
                f_iter *= f
            f *= f
        return f_iter

    def enumerate_cycles(self):
        """Generate f's cycle decomposition in O(len(f)) time"""
        Tried = set()
        CycleEls = set()
        Remaining = set(self.domain)
        while Remaining:
            x = Remaining.pop()
            path = [x]
            while x not in Tried:
                Remaining.discard(x)
                Tried.add(x)
                x = self[x]
                path.append(x)
            if x not in CycleEls:
                cycle = path[path.index(x)+1:]
                if cycle:
                    yield cycle
                    CycleEls.update(cycle)

    @cached_property
    def cycles(self):
        """Return the set of f's cycles"""
        return frozenset(map(tuple, self.enumerate_cycles()))

    @cached_property
    def limitset(self):
        """x in f.limitset <==> any(x in cycle for cycle in f.cycles)"""
        return frozenset(itertools.chain.from_iterable(self.cycles))

    @cached_property
    def attached_treenodes(self):
        """f.attached_treenodes[y] <==> f.preimage[y] - f.limitset"""
        descendants = [set() for _ in range(len(self))]
        for x, inv_image in enumerate(self.preimage):
            for f in inv_image:
                if f not in self.limitset:
                    descendants[x].add(f)
        return tuple(map(frozenset, descendants))

    def _attached_level_sequence(self, node, level=0):
        """Return the level sequence of the rooted tree formed from the graph
        of all noncyclic nodes whose iteration paths pass through node"""
        level_sequence = [level]
        for x in self.attached_treenodes[node]:
            level_sequence.extend(self._attached_level_sequence(x, level+1))
        return level_sequence


def randfunc(n):
    """ Return a random endofunction on n elements. """
    return Endofunction(random.randrange(n) for _ in range(n))


class SymmetricFunction(Endofunction):
    """ An invertible endofunction. """

    def __new__(cls, func):
        self = super(SymmetricFunction, cls).__new__(cls, func)
        if len(self) != len(self.image):
            raise ValueError("This function is not invertible.")
        return self

    def __rmul__(self, other):
        """s.__rmul__(f) = f * s"""
        return other.__class__(other[x] for x in self)

    def __pow__(self, n):
        """Symmetric functions allow us to take inverses."""
        if n >= 0:
            return Endofunction.__pow__(self, n)
        else:
            return Endofunction.__pow__(self.inverse, -n)

    @cached_property
    def inverse(self):
        """s.inverse <==> s**-1"""
        # Code taken directly from: "Inverting permutations in Python" at
        # http://stackoverflow.com/a/9185908.
        inv = [0]*len(self)
        for x, y in enumerate(self):
            inv[y] = x
        return self.__class__(inv)

    def conj(self, f):
        """s.conj(f) <==> s * f * s.inverse"""
        # Order of conjugation matters. Take the trees:
        #   1   2          a   b
        #    \ /    <==>    \ /
        #     3              c
        # whose nodes may be mapped to each other by:
        #   s(1) = a
        #   s(2) = b
        #   s(3) = c.
        # If f(1) = f(2) = f(3) = 3, and g(a) = g(b) = g(c) = c, then f is
        # related to g:  g(x) = s(f(s^-1(x))). We view conjugation *of* f as a
        # way to get *to* g.
        g = [0]*len(f)
        for x, y in enumerate(self):
            g[y] = self[f[x]]
        return f.__class__(g)


def randperm(n):
    """Return a random permutation of range(n)."""
    r = list(range(n))  # Explicitly call list for python 3 compatibility.
    random.shuffle(r)
    return SymmetricFunction(r)


def randconj(f):
    """Return a random conjugate of f."""
    return randperm(len(f)).conj(f)


class TransformationMonoid(bases.Enumerable):
    """Set of all endofunctions on n elements."""

    def __init__(self, set_size):
        super(TransformationMonoid, self).__init__(set_size, None, 0)

    def __iter__(self):
        for func in productrange.productrange([self.n] * self.n):
            yield Endofunction(func)

    def __len__(self):
        return self.n ** self.n