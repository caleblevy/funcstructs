"""Data structures for representing endofunctions: mappings from a finite set
into itself.

Caleb Levy, 2015.
"""

import random

from . import bases, productrange
from .utils import cached_property, flatten
from ..prototypes import treefuncs

__all__ = [
    "Endofunction", "SymmetricFunction",
    "randfunc", "randperm", "randconj",
    "TransformationMonoid"
]


class Endofunction(bases.Tuple):
    """Implementation of an endofunction as a map of range(N) into itself using
    a list."""

    from_levels = treefuncs.from_levels

    def __str__(self):
        funcstring = self.__class__.__name__+'([\n'
        mapvals = []
        for x, y in enumerate(self[:-1]):
            mapvals.append('\t'+str(x)+' -> '+str(y)+', \n')
        funcstring += ''.join(mapvals)
        funcstring += '\t'+str(len(self)-1)+" -> "+str(self[-1])+'\n])'
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
        for x, y in enumerate(self):
            preim[y].add(x)
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
        return frozenset(flatten(self.cycles))

    @cached_property
    def acyclic_ancestors(self):
        """f.attached_treenodes[y] <==> f.preimage[y] - f.limitset"""
        descendants = [set() for _ in range(len(self))]
        for x, inv_image in enumerate(self.preimage):
            for f in inv_image:
                if f not in self.limitset:
                    descendants[x].add(f)
        return tuple(map(frozenset, descendants))


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
