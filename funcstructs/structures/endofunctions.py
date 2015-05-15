"""Data structures for representing endofunctions: mappings from a finite set
into itself.

Caleb Levy, 2015.
"""

import random
from collections import defaultdict

from . import bases, productrange
from . import _treefuncs
from .utils import cached_property, flatten

__all__ = [
    "Endofunction", "SymmetricFunction",
    "randfunc", "randperm", "randconj",
    "TransformationMonoid"
]


class Function(bases.frozendict):
    """An immutable mapping between sets."""

    @classmethod
    def _new(cls, *args, **kwargs):
        # Bypass all verification and directly call Function constructor
        return super(Function, cls).__new__(cls, *args, **kwargs)

    def __new__(cls, *args, **kwargs):
        return cls._new(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        _ = self.image  # Ensure elements of the image are hashable

    def __iter__(self):
        """Return elements of the domain and their labels in pairs"""
        return iter(self.items())

    @cached_property
    def domain(self):
        """The set of objects for which f[x] is defined"""
        return frozenset(self.keys())

    @cached_property
    def image(self):
        """f.image <==> {f[x] for x in f.domain}"""
        return frozenset(self.values())

    @cached_property
    def preimage(self):
        """f.preimage[y] <==> {x for x in f.domain if f[x] == y}"""
        preim = defaultdict(set)
        for x, y in self:
            preim[y].add(x)
        return bases.frozendict((x, frozenset(preim[x])) for x in self.domain)

    def __mul__(self, other):
        """(f * g)[x] <==> f[g[x]]"""
        # f * g becomes a function on g's domain, so it inherits class of g
        return other.__class__((x, self[y]) for x, y in other)


class Bijection(Function):
    """An invertible Function."""

    def __init__(self, *args, **kwargs):
        super(Bijection, self).__init__(*args, **kwargs)
        # Check cardinality of domain and codomain are identical
        if len(self) != len(self.image):
            raise ValueError("This function is not invertible.")

    def __rmul__(self, other):
        """s.__rmul__(f) = f * s"""
        return other.__class__((x, other[y]) for x, y in self)

    @cached_property
    def inverse(self):
        """s.inverse <==> s**-1"""
        # Code taken directly from: "Inverting permutations in Python" at
        # http://stackoverflow.com/a/9185908.
        return self.__class__((y, x) for x, y in self)

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
        return f.__class__((y, self[f[x]]) for x, y in self)


class Endofunction(Function):
    """A Function whose domain contains its codomain."""

    def __init__(self, *args, **kwargs):
        super(Endofunction, self).__init__(*args, **kwargs)
        if not self.domain.issuperset(self.image):
            raise ValueError("image must be a subset of the domain")

    @classmethod
    def from_levels(cls, levels):
        """Make an endofunction representing a tree."""
        return cls((x, y) for x, _, y in
                   _treefuncs.funclevels_iterator(levels))

    def __pow__(self, n):
        """f**n <==> the nth iterate of f"""
        # Convert to string of binary digits, clip off 0b, then reverse.
        component_iterates = bin(n)[2::][::-1]
        f = self
        f_iter = self.__class__((x, x) for x in self.domain)
        # Iterate by self-composing, akin to exponentiation by squaring.
        for it in component_iterates:
            if it == '1':
                f_iter *= f
            f *= f
        return f_iter

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
        return frozenset(flatten(self.cycles))

    @cached_property
    def acyclic_ancestors(self):
        """f.attached_treenodes[y] <==> f.preimage[y] - f.limitset"""
        descendants = defaultdict(set)
        for y, inv_image in self.preimage.items():
            for x in inv_image:
                if x not in self.limitset:
                    descendants[y].add(x)
        return bases.frozendict((x, frozenset(descendants[x])) for x in
                                self.domain)


class SymmetricFunction(Endofunction, Bijection):
    """A Bijective Endofunction"""

    def __init__(self, *args, **kwargs):
        super(SymmetricFunction, self).__init__(*args, **kwargs)

    def __pow__(self, n):
        """Symmetric functions allow us to take inverses."""
        if n >= 0:
            return super(SymmetricFunction, self).__pow__(n)
        else:
            return super(SymmetricFunction, self.inverse).__pow__(-n)


# Convenience functions for defining Endofunctions from a sequence in range(n)


def rangefunc(seq):
    """Return an Endofunction defined on range(len(seq))"""
    return Endofunction(enumerate(seq))


def rangeperm(seq):
    """Return a symmetric function defined on range(len(seq))"""
    return SymmetricFunction(enumerate(seq))


# Convenience functions for return random Functions


def randfunc(n):
    """ Return a random endofunction on n elements. """
    return rangefunc(random.randrange(n) for _ in range(n))


def randperm(n):
    """Return a random permutation of range(n)."""
    r = list(range(n))  # Explicitly call list for python 3 compatibility.
    random.shuffle(r)
    return rangeperm(r)


def randconj(f):
    """Return a random conjugate of f."""
    return randperm(len(f)).conj(f)


# Function enumerators


class TransformationMonoid(bases.Enumerable):
    """Set of all endofunctions on n elements."""

    def __init__(self, set_size):
        super(TransformationMonoid, self).__init__(set_size, None, 0)

    def __iter__(self):
        for func in productrange.productrange([self.n] * self.n):
            yield rangefunc(func)

    def __len__(self):
        return self.n ** self.n
