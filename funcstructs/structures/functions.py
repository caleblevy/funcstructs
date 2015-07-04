"""Data structures for representing mappings between sets.

Caleb Levy, 2015.
"""

import itertools
import random
from collections import defaultdict
from math import factorial

from funcstructs import compat

from funcstructs.bases import frozendict, Enumerable


def _result_functype(f, g):
    """Coerce func types of f and g into the proper type.

    Rules are:
    ----------
    1) If both types are the same, so is their result
    2) Function has highest priority
    3) SymmetricFunction has lowest priority
    4) Bijection and Endofunction result in Function
    """
    functypes = {type(f), type(g)}
    if len(functypes) == 1:
        return functypes.pop()
    elif Function in functypes:
        return Function
    elif SymmetricFunction in functypes:
        return (functypes - {SymmetricFunction}).pop()
    return Function


def _parsed_domain(domain):
    """Change domain to a frozenset. If domain is int, set to range(domain)."""
    if domain is None:
        domain = ()
    elif isinstance(domain, int):
        if domain < 0:
            raise ValueError("Cannot define domain on %s elements" % domain)
        domain = range(domain)
    return frozenset(domain)


def identity(domain=None):
    """Return the identity function on a given domain."""
    S = _parsed_domain(domain)
    return SymmetricFunction(zip(S, S))


class Function(frozendict):
    """An immutable mapping between sets."""

    __slots__ = ()

    def __init__(*args, **kwargs):
        _ = args[0].image  # make sure that codomain is hashable

    # "domain" and "image" used to be attributes computed in the constructor
    # and cached for speed, with corresponding __slots__ and a WriteOnceMixin
    # to prevent altering them. There are two reasons for using properties:
    #
    # 1) Multiply inheriting from classes with nonempty __slots__ leads to
    #    instance layout conflicts in jython, *even with identical base slots*
    #    (instance layout conflicts are *expected* when multiple bases have
    #    *different* slots).
    #
    # 2) It turned out that after testing in CPython that computing on the fly
    #    was faster anyway, presumably due to decreased memory overhead.

    @property
    def domain(self):
        """f.domain <==> {x for (x, y) in f}"""
        return frozenset(self.keys())

    @property
    def image(self):
        """f.image <==> {y for (x, y) if f}"""
        return frozenset(self.values())

    __call__ = dict.__getitem__

    @classmethod
    def __getitem__(cls, *args, **kwargs):
        raise TypeError("%s should be evaluated by calling" % cls.__name__)

    # Mathematical functions describe a set of pairings of points; returning
    # elements of the domain does not provide useful information; only the
    # key-value pairs matter, so __iter__ is overridden to dict.__items__.

    def __iter__(self):
        """Return elements of the domain and their labels in pairs"""
        return iter(self.items())

    def __contains__(self, item):
        """Test whether f contains a key-value pair."""
        return item in compat.viewitems(self)

    # Define composition of Functions

    def __mul__(self, other):
        """(f * g)(x) <==> f(g(x))"""
        # f * g becomes a function on g's domain, so it inherits class of g
        return _result_functype(self, other)((x, self(y)) for x, y in other)

    def preimage(self):
        """f.preimage[y] <==> {x for x in f.domain if f(x) == y}"""
        preim = defaultdict(list)
        for x, y in self:
            preim[y].append(x)
        return frozendict((y, frozenset(preim[y])) for y in self.image)


class Bijection(Function):
    """An invertible Function.

    Bijection objects have an inverse method. For every Bijection b:

    >>> b.inverse() * b == identity(b.domain)
    True
    >>> b * b.inverse() == identity(b.image)
    True

    Bijections can also conjugate functions:

    >>> b.conj(f) = type(f)(b * f * b.inverse())
    """

    __slots__ = ()

    def __init__(*args, **kwargs):
        self = args[0]
        super(Bijection, self).__init__(*args, **kwargs)
        # Check cardinality of domain and codomain are identical
        if len(self) != len(self.image):
            raise ValueError("This function is not invertible.")

    def inverse(self):
        """s.inverse() * s <==> identity(s.domain)"""
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
        return f.__class__((y, self(f(x))) for x, y in self)


class Endofunction(Function):
    """A Function whose domain contains its codomain."""

    __slots__ = ()

    def __init__(*args, **kwargs):
        self = args[0]
        super(Endofunction, self).__init__(*args, **kwargs)
        if not self.domain.issuperset(self.image):
            raise ValueError("image must be a subset of the domain")

    def __pow__(self, n):
        """f**n <==> the nth iterate of f"""
        f = self
        f_iter = identity(self.domain)
        # Decompose f**n into the composition of power-of-2 iterates, akin to
        # exponentiation by squaring.
        for it in bin(n)[-1:1:-1]:
            if it == '1':
                f_iter *= f
            f *= f
        return f_iter

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
        tried = set()
        cyclic = set()
        remaining = set(self.domain)
        while remaining:
            x = remaining.pop()
            path = [x]
            while x not in tried:
                remaining.discard(x)
                tried.add(x)
                x = self(x)
                path.append(x)
            if x not in cyclic:
                cycle = path[path.index(x)+1:]
                if cycle:
                    yield cycle
                    cyclic.update(cycle)

    def cycles(self):
        """Return the set of f's cycles"""
        return frozenset(map(tuple, self.enumerate_cycles()))

    def limitset(self):
        """x in f.limitset <==> any(x in cycle for cycle in f.cycles)"""
        return frozenset(itertools.chain(*self.cycles()))

    def acyclic_ancestors(self):
        """f.attached_treenodes[y] <==> f.preimage[y] - f.limitset"""
        descendants = defaultdict(list)
        lim = self.limitset()  # make local copy for speed
        for y, inv_image in self.preimage().items():
            for x in inv_image:
                if x not in lim:
                    descendants[y].append(x)
        return frozendict((x, frozenset(descendants[x])) for x in self.domain)


class SymmetricFunction(Endofunction, Bijection):
    """A Bijective Endofunction"""

    __slots__ = ()

    def __pow__(self, n):
        """Symmetric functions allow us to take inverses."""
        if n >= 0:
            return super(SymmetricFunction, self).__pow__(n)
        else:
            return super(SymmetricFunction, self.inverse()).__pow__(-n)


# Convenience functions for defining Endofunctions from a sequence in range(n)


def rangefunc(seq):
    """Return an Endofunction defined on range(len(seq))."""
    return Endofunction(enumerate(seq))


def rangeperm(seq):
    """Return a symmetric function defined on range(len(seq))."""
    return SymmetricFunction(enumerate(seq))


# Convenience functions for returning random Functions


def randfunc(domain, codomain=None):
    """Return a random endofunction on a domain."""
    S = list(_parsed_domain(domain))
    if codomain is not None:
        T = list(_parsed_domain(codomain))
        result_type = Function
    else:
        T = S
        result_type = Endofunction
    return result_type((x, random.choice(T)) for x in S)


def randperm(domain, codomain=None):
    """Return a random permutation of range(n)."""
    S = list(_parsed_domain(domain))
    if codomain is not None:
        T = list(_parsed_domain(codomain))
        result_type = Bijection
    else:
        T = S[:]
        result_type = SymmetricFunction
    random.shuffle(T)
    return result_type(zip(S, T))


def randconj(f, newdomain=None):
    """Return a random conjugate of f."""
    if newdomain is None:
        return randperm(f.domain).conj(f)
    else:
        return randperm(f.domain, _parsed_domain(newdomain)).conj(f)


# Function enumerators


class Mappings(Enumerable):
    """The set of Functions between a domain and a codomain"""

    def __init__(self, domain, codomain):
        self.domain = _parsed_domain(domain)
        self.codomain = _parsed_domain(codomain)

    def __iter__(self):
        domain, codomain = map(sorted, [self.domain, self.codomain])
        for f in itertools.product(codomain, repeat=len(domain)):
            yield Function(zip(domain, f))

    def __len__(self):
        return len(self.codomain) ** len(self.domain)


class Isomorphisms(Enumerable):
    """The set of bijections between a domain and a codomain"""

    def __init__(self, domain, codomain):
        domain = _parsed_domain(domain)
        codomain = _parsed_domain(codomain)
        if len(domain) != len(codomain):
            raise ValueError("Sets of size %s and %s cannot be isomorphic" % (
                len(domain), len(codomain)))
        self.domain = domain
        self.codomain = codomain

    def __iter__(self):
        domain, codomain = map(sorted, [self.domain, self.codomain])
        for p in itertools.permutations(codomain):
            yield Bijection(zip(domain, p))

    def __len__(self):
        return factorial(len(self.domain))


class TransformationMonoid(Enumerable):
    """Set of all Endofunctions on a domain."""

    def __init__(self, domain):
        self.domain = _parsed_domain(domain)

    def __iter__(self):
        domain = sorted(self.domain)
        for f in itertools.product(domain, repeat=len(domain)):
            yield Endofunction(zip(domain, f))

    def __len__(self):
        return len(self.domain) ** len(self.domain)


class SymmetricGroup(Enumerable):
    """The set of automorphisms on a domain"""

    def __init__(self, domain):
        self.domain = _parsed_domain(domain)

    def __iter__(self):
        domain = sorted(self.domain)
        for p in itertools.permutations(domain):
            yield SymmetricFunction(zip(domain, p))

    def __len__(self):
        return factorial(len(self.domain))
