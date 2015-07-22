"""Data structures for representing mappings between sets.

Caleb Levy, 2015.
"""

import itertools
import random
from collections import defaultdict
from math import factorial

from funcstructs import compat

from funcstructs.bases import frozendict, Enumerable
from platform import python_implementation


def _result_functype(f, g):
    """Determine the appropriate output type for f * g.

    Rules are:
    ----------
    1) If both types are the same, so is their result
    2) Function has highest priority
    3) Permutation has lowest priority
    4) Bijection and Endofunction result in Function
    """
    functypes = {type(f), type(g)}
    if len(functypes) == 1:
        return functypes.pop()
    elif Function in functypes:
        return Function
    elif Permutation in functypes:
        return (functypes - {Permutation}).pop()
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
    return Permutation(zip(S, S))


class Function(frozendict):
    """An immutable mapping between sets.

    Function mapping objects reflect their mathematical counterparts: a
    mapping f: A -> B is a subset of the Cartesian product AxB such that
    there is precisely one element in f for each x in A.

    >>> f = Function(a=1, b=1, c=1)             # construct Functions in the
    >>> g = Function({1: 'a', 2: 'a', 3: 'a'})  # same ways as dicts.
    >>> f == Function.fromkeys("abc", 1)
    True

    >>> Function(a=[1])                         # Functions must be hashable
    ...
    TypeError

    >>> f * g                                   # Functions can be composed
    Function({1: 1, 2: 1, 3: 1})
    >>> g * f
    Function({'a': 'a', 'c': 'a', 'b': 'a'})

    >>> f['a']                                  # Functions are evaluated by
    1                                           # using the dict interface
    >>> g[f['b']]
    'a'

    >>> list(f)                                 # iteration returns
    [('a', 1), ('c', 1), ('b', 1)]              # key-value pairs
    >>> 'a' in f
    False
    >>> ('a', 1) in f                           # containment reflects
    True                                        # iteration
    """

    __slots__ = ()

    if python_implementation() == "Jython":
        # Jython reports instance layout conflicts if class with __slots__
        # not inheriting from a builtin appears multiple times in the
        # class inheritance tree. Related to http://bugs.jython.org/issue2101
        # and http://bugs.jython.org/issue1996.
        __slots__ += '__dict__',

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

    # Mathematical functions describe a set of pairings of points; returning
    # elements of the domain does not provide useful information; only the
    # key-value pairs matter, so __iter__ is overridden to dict.__items__.

    def __iter__(self):
        """iter(f) <==> (x, f[x]) for x in f.domain"""
        return iter(self.items())

    def __contains__(self, item):
        """(x, y) in f <==> f[x] == y"""
        return item in self.items()

    # Define composition of Functions

    def __mul__(self, other):
        """(f * g)(x) <==> f[g[x]]"""
        # f * g becomes a function on g's domain, so it inherits class of g
        return _result_functype(self, other)((x, self[y]) for x, y in other)

    # Design Note: Function objects used to be callable; their __call__ method
    # was set to dict.__getitem__ and __getitem__ itself was disabled.
    #
    # When Function was an explicit subclass of the builtin dict, the dict
    # constructor could handle Function objects since it would directly call
    # the C API for copying.
    #
    # Once frozendict became a proxy to a dict, however, python would default
    # to the (inadequately documented) convention for dict constructors, where
    # calling "dict(obj)" decides if obj is a mapping by checking for the
    # presence of a "keys" method, and if so acquires the values using
    # __getitem__. (See "overloaded __iter__ is bypassed when deriving from
    # dict" at http://stackoverflow.com/q/18317905/3349520). This broke the
    # ability to copy Functions to dicts.
    #
    # More important, this will break any code relying on the normal dict
    # interface, causing potentially massive inconvenience. It further obscures
    # the difference between Function objects and python "functions" which
    # represent very different *kinds* of function.
    #
    # The sole benefit was providing syntactic similarity between Functions and
    # mathematical mappings, at the cost of semantic consistency.
    #
    # Leaving both methods in would clearly introduce ambiguity into the API,
    # and getting rid of the __call__ syntax alleviates a fair number of
    # headaches.

    @property
    def fibers(self):
        """f.fibers[y] <==> {x for x in f.domain if f[x] == y}"""
        # TODO: Add preimage class
        preim = defaultdict(list)
        for x, y in self:
            preim[y].append(x)
        return frozendict((y, frozenset(preim[y])) for y in self.image)


class Bijection(Function):
    """An invertible Function.

    Bijection objects have an inverse method. For every Bijection b,
    - b.inverse * b == identity(b.domain)
    - b * b.inverse == identity(b.image)

    They can also conjugate functions:
    - b.conj(f) == b * f * b.inverse()
    """
    # TODO: add examples of the above

    __slots__ = ()

    def __init__(*args, **kwargs):
        self = args[0]
        super(Bijection, self).__init__(*args, **kwargs)
        # Check cardinality of domain and codomain are identical
        if len(self) != len(self.image):
            raise ValueError("This function is not invertible.")

    @property
    def inverse(self):
        """s.inverse * s <==> identity(s.domain)"""
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
    """A Function whose domain contains its codomain.

    Endofunctions support iteration using exponential notation.

    >>> f = Endofunction({0: 0, 1: 0, 2: 1, 3: 2})
    >>> f**2
    Endofunction({0: 0, 1: 0, 2: 0, 3: 1})
    >>> f**3
    Endofunction({0: 0, 1: 0, 2: 0, 3: 0})
    >>> f**0
    >>> Permutation({0: 0, 1: 1, 2: 2, 3: 3})  # identity iterate

    Iteration can be used to form cycles.

    >>> f.cycles
    frozenset([(0,)])
    """

    __slots__ = ()

    def __init__(*args, **kwargs):
        self = args[0]
        super(Endofunction, self).__init__(*args, **kwargs)
        if not self.domain.issuperset(self.image):
            raise ValueError("image must be a subset of the domain")

    def __pow__(self, n):
        """f**n <==> the nth iterate of f (n > 0)"""
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
        """f.imagepath()[n] <==> len((f**n).image)"""
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

    @property
    def cycles(self):
        """Return the set of f's cycles"""
        tried = set()
        cyclic = set()
        remaining = set(self.domain)
        cycles = []
        while remaining:
            x = remaining.pop()
            path = [x]
            while x not in tried:
                remaining.discard(x)
                tried.add(x)
                x = self[x]
                path.append(x)
            if x not in cyclic:
                cycle = path[path.index(x)+1:]
                if cycle:
                    cycles.append(cycle)
                    cyclic.update(cycle)
        return frozenset(map(tuple, cycles))

    @property
    def limitset(self):
        """x in f.limitset <==> any(x in cycle for cycle in f.cycles)"""
        return frozenset(itertools.chain(*self.cycles))

    @property
    def acyclic_ancestors(self):
        """f.acyclic_ancestors[y] <==> f.fibers[y] - f.limitset"""
        descendants = defaultdict(list)
        lim = self.limitset  # make local copy for speed
        for y, inv_image in self.fibers.items():
            for x in inv_image:
                if x not in lim:
                    descendants[y].append(x)
        return frozendict((x, frozenset(descendants[x])) for x in self.domain)


class Permutation(Endofunction, Bijection):
    """A invertible Endofunction.

    Permutations can be iterated like Endofunctions and inverted like
    Bijections. Since a Permutation inverse is itself a Permutation, we
    can define exponentiation of Permutations over all integers. Permutation
    objects on a given domain thus form a group.

    >>> s = Permutation({0: 1, 1: 2, 2: 3, 3: 0, 4: 5, 5: 6, 6: 4})
    >>> s**-2
    Permutation({0: 2, 1: 3, 2: 0, 3: 1, 4: 5, 5: 6, 6: 4})

    >>> s**-2 == (s.inverse())**2
    True
    >>> s * s**-1 == s**-1 * s == identity(s.domain)
    True
    """

    __slots__ = ()

    def __pow__(self, n):
        """f**n <==> the nth iterate of f"""
        if n >= 0:
            return super(Permutation, self).__pow__(n)
        else:
            return super(Permutation, self.inverse).__pow__(-n)


# Convenience functions for defining Endofunctions from a sequence in range(n)


def rangefunc(seq):
    """Return an Endofunction defined on range(len(seq))."""
    return Endofunction(enumerate(seq))


def rangeperm(seq):
    """Return a symmetric function defined on range(len(seq))."""
    return Permutation(enumerate(seq))


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
        result_type = Permutation
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
    """Mappings(A, B) -> The set of Functions from set A to B.

    >>> m = Mappings("ab", range(3))    # domains can be any iterable
    >>> list(m)
    [Function({'a': 0, 'b': 0}), Function({'a': 0, 'b': 1}),
    Function({'a': 0, 'b': 2}), Function({'a': 1, 'b': 0}),
    Function({'a': 1, 'b': 1}), Function({'a': 1, 'b': 2}),
    Function({'a': 2, 'b': 0}), Function({'a': 2, 'b': 1}),
    Function({'a': 2, 'b': 2})]

    >>> len(m)                          # m has len(B) ** len(A) elements
    9
    """

    def __init__(self, domain, codomain):
        self.domain = _parsed_domain(domain)
        self.codomain = _parsed_domain(codomain)

    def __iter__(self):
        domain, codomain = map(sorted, [self.domain, self.codomain])
        for f in itertools.product(codomain, repeat=len(domain)):
            yield Function(zip(domain, f))

    def __contains__(self, other):
        if isinstance(other, Function):
            return self.domain == other.domain and \
                other.image.issubset(self.codomain)
        return False

    def __len__(self):
        return len(self.codomain) ** len(self.domain)


class Isomorphisms(Enumerable):
    """Isomorphisms(A, B) -> The set of bijections between A and B

    >>> i = Isomorphisms("abc", range(3))
    >>> list(i)
    [Bijection({'a': 0, 'c': 2, 'b': 1}), Bijection({'a': 0, 'c': 1, 'b': 2}),
    Bijection({'a': 1, 'c': 2, 'b': 0}), Bijection({'a': 1, 'c': 0, 'b': 2}),
    Bijection({'a': 2, 'c': 1, 'b': 0}), Bijection({'a': 2, 'c': 0, 'b': 1})]

    >>> len(i)                          # i has factorial(len(A)) elements
    6
    """

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

    def __contains__(self, other):
        if isinstance(other, Bijection):
            return self.domain == other.domain and self.codomain == other.image
        return False

    def __len__(self):
        return factorial(len(self.domain))


class TransformationMonoid(Enumerable):
    """TransformationMonoid(A) -> The set of Endofunctions on A

    >>> t = TransformationMonoid(2)
    >>> list(t)
    [Endofunction({0: 0, 1: 0}), Endofunction({0: 0, 1: 1}),
    Endofunction({0: 1, 1: 0}), Endofunction({0: 1, 1: 1})]

    >>> len(t)                          # t has len(A)**len(A) elements
    4
    """

    def __init__(self, domain):
        self.domain = _parsed_domain(domain)

    def __iter__(self):
        domain = sorted(self.domain)
        for f in itertools.product(domain, repeat=len(domain)):
            yield Endofunction(zip(domain, f))

    def __contains__(self, other):
        if isinstance(other, Endofunction):
            return self.domain == other.domain
        return False

    def __len__(self):
        return len(self.domain) ** len(self.domain)


class SymmetricGroup(Enumerable):
    """SymmetricGroup(A) -> The set of Permutations of A

    >>> s = SymmetricGroup(3)
    >>> list(s)
    [Permutation({0: 0, 1: 1, 2: 2}),
    Permutation({0: 0, 1: 2, 2: 1}),
    Permutation({0: 1, 1: 0, 2: 2}),
    Permutation({0: 1, 1: 2, 2: 0}),
    Permutation({0: 2, 1: 0, 2: 1}),
    Permutation({0: 2, 1: 1, 2: 0})]

    >>> len(s)                          # s has factorial(len(A)) elements
    6
    """

    def __init__(self, domain):
        self.domain = _parsed_domain(domain)

    def __iter__(self):
        domain = sorted(self.domain)
        for p in itertools.permutations(domain):
            yield Permutation(zip(domain, p))

    def __contains__(self, other):
        if isinstance(other, Permutation):
            return self.domain == other.domain
        return False

    def __len__(self):
        return factorial(len(self.domain))
