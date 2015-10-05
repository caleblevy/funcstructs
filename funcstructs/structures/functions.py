"""Data structures for representing mappings between sets.

Caleb Levy, 2015.
"""

import itertools
import random
from collections import defaultdict
from functools import partial
from math import factorial
from platform import python_implementation

from funcstructs.compat import is_index
from funcstructs.bases import frozendict, Enumerable, typecheck
from funcstructs.bases.frozendict import _map_accessors


def _parsed_domain(domain):
    """Change domain to a frozenset. If domain is int, set to range(domain)."""
    if domain is None:
        domain = ()
    if is_index(domain):
        if domain < 0:
            raise ValueError("Cannot define domain on %s elements" % domain)
        domain = range(domain)
    return frozenset(domain)


def identity(domain=None):
    """Return the identity function on a given domain."""
    S = _parsed_domain(domain)
    return Permutation(zip(S, S))


def _FunctionHelper(fcls):
    """Helper for making the Functional mapping type."""

    map_set, map_get = _map_accessors()

    @staticmethod
    def __new__(*args, **kwargs):
        cls = args[0]
        mapping = dict(*args[1:], **kwargs)
        im = frozenset(mapping.values())
        invertible = len(im) == len(mapping)
        endomorphic = im.issubset(mapping.keys())
        if invertible and endomorphic:
            functype = Permutation
        elif invertible:
            functype = Bijection
        elif endomorphic:
            functype = Endofunction
        else:
            functype = Function
        # Function, Bijection, Endofunction and Permutation should
        # collectively be thought of as "Function". Inputs are promoted
        # to the most derived type automatically, since ultimately,
        # (i.e.) any Function with image the size of its domain is a
        # Bijection, whether that is its type or not, so we may as well
        # instantiate it as such and endow it with the usual methods.
        #
        # The only purpose in calling Endofunction / Bijection /
        # Permutation directly is imposing a check for what you believe
        # they should be, in the same spirit as (i.e.) a list vs tuple
        # makes no difference if you never change the list (and don't
        # need to hash it), but if you expect it to be immutable, you
        # should use a tuple.
        #
        # None of these four are meant to be subclassed. Although there
        # are many types of Function (for example, group and ring
        # operations), the "Function" data type is fundamentally designed
        # to reflect simple correspondences between finite sets in
        # memory. (This is why Multiset is not a Function subtype;
        # Multisets have a different structure and semantic meaning from
        # regular Functions).
        #
        # TODO: Incorporate the above comments into some form of
        # documentation.
        #
        # TODO: Unittest that none of these four classes can have
        # instantiable subclasses.
        #
        # TODO: I remain undecided on whether Function and its subclasses
        # should receive their own metaclass. The current structure
        # should not allow for *instantiating* subclasses, in which case
        # there is little sense in allowing such subclasses at all.
        #
        # Since the purpose of this metaclass would be disallowing (new)
        # Function subclasses, we need not consider the (usual) metaclass
        # conflict problems. My main concern is that there is
        # no "is-a" relationship here; a Function isn't a different
        # kind of class (unlike, i.e. ParamMeta, which characterizes
        # object types with a very particular structure).
        #
        # Ultimately, I think a class rename ("Correspondence") along
        # with a small "SemiFinal" metaclass will be the appropriate answer,
        # or just eliminate the various Function subclasses all together.
        # Even sympy hasn't achieved the lofty goal of placing all of math's
        # important kinds of function into a tidy framework, and my goals
        # are (for now) much more limited, so YAGNI will apply, and from
        # an API consistency standpoint a small metaclass will get the job
        # done.
        if not issubclass(functype, cls):
            raise TypeError("Input mapping is not %s" % cls.__name__)
        self = object.__new__(functype)
        map_set(self, mapping)
        return self
    fcls.__new__ = __new__

    global _FunctionHelper
    del _FunctionHelper

    return fcls


@_FunctionHelper
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

    # In mathematics, the domain is an inherent property of a function.

    @property
    def domain(self):
        """f.domain <==> {x for (x, y) in f}"""
        return self._keys()

    # Images, on the other hand, must be computed by evaluating f either
    # on the whole domain or the given subset, thus Function.image() is a
    # method.

    def image(self):
        """f.image() <==> {y for (x, y) if f}"""
        return frozenset(self._values())

    # Mathematical functions describe a set of pairings of points; returning
    # elements of the domain does not provide useful information; only the
    # key-value pairs matter, so __iter__ is overridden to dict.__items__.

    def __iter__(self):
        """iter(f) <==> (x, f[x]) for x in f.domain"""
        return iter(self._items())

    def __contains__(self, item):
        """(x, y) in f <==> f[x] == y"""
        return item in self._items()

    # Define composition of Functions

    def __mul__(self, other):
        """(f * g)[x] <==> f[g[x]]"""
        return Function((x, self[y]) for x, y in other)

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
        return frozendict((y, frozenset(preim[y])) for y in self.image())


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

    def __pow__(self, n):
        """f**n <==> the nth iterate of f (n > 0)"""
        f = self
        f_iter = Permutation(zip(self.domain, self.domain))
        # Decompose f**n into the composition of power-of-2 iterates, akin to
        # exponentiation by squaring.
        for it in bin(n)[-1:1:-1]:
            if it == '1':
                f_iter *= f
            f *= f
        return f_iter

    # TODO: eliminate this method, or use it only for testing
    # ConjugacyClass.imagepath
    def imagepath(self):
        """f.imagepath()[n] <==> len((f**n).image)"""
        cardinalities = [len(self.image())]
        f = self
        card_prev = len(self)
        for it in range(1, len(self)-1):
            f *= self
            card = len(f.image())
            cardinalities.append(card)
            # Save some time; if we have reached the fixed set, return.
            if card == card_prev:
                cardinalities.extend([card]*(len(self)-2-it))
                break
            card_prev = card
        return tuple(cardinalities)

    def cycles(self):
        """Return the set of f's cycles"""
        # Algorithm runs in O(len(self))
        tried = set()
        remaining = set(self.domain)
        cycles = []
        while remaining:
            x = remaining.pop()
            path = [x]
            i = 0
            index = {x: i}
            while x not in tried:
                remaining.discard(x)
                tried.add(x)
                x = self[x]
                if x not in index:
                    path.append(x)
                    i += 1
                    index[x] = i
                else:
                    cycles.append(path[index[x]:])
                    break
        return frozenset(map(tuple, cycles))

    @property
    def limitset(self):
        """x in f.limitset <==> any(x in cycle for cycle in f.cycles)"""
        return frozenset(itertools.chain(*self.cycles()))

    @property
    def acyclic_ancestors(self):
        """f.acyclic_ancestors[y] <==> f.fibers[y] - f.limitset"""
        descendants = defaultdict(list)
        lim = self.limitset  # make local copy for speed
        for y, inv_image in self.fibers._items():
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


def rangefunc(seq):
    """Return an Endofunction defined on range(len(seq))."""
    return Function(enumerate(seq))


def randfunc(domain, codomain=None, invertible=False):
    """Return a random Function from domain to codomain."""
    S = list(_parsed_domain(domain))
    T = S if codomain is None else list(_parsed_domain(codomain))
    if invertible and len(S) != len(T):
        raise TypeError("Cannot make isomorphism between %s and %s" % (S, T))
    if not invertible:
        return Function((x, random.choice(T)) for x in S)
    else:
        T = T[:]
        random.shuffle(T)
        return Function(zip(S, T))


randperm = partial(randfunc, invertible=True)


def randconj(f, newdomain=None):
    """Return a random conjugate of f."""
    return randperm(f.domain, newdomain).conj(f)


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

    def __init__(self, domain, codomain=None, invertible=False):
        domain = _parsed_domain(domain)
        codomain = domain if codomain is None else _parsed_domain(codomain)
        invertible = bool(invertible)
        if invertible and len(domain) != len(codomain):
            raise TypeError("No isomorphisms between %s and %s" % (
                            domain, codomain))
        self.domain = domain
        self.codomain = codomain
        self.invertible = invertible

    def __iter__(self):
        try:
            domain, codomain = map(sorted, [self.domain, self.codomain])
        except TypeError:
            domain, codomain = map(tuple, [self.domain, self.codomain])
        if not self.invertible:
            for f in itertools.product(codomain, repeat=len(domain)):
                yield Function(zip(domain, f))
        else:
            for f in itertools.permutations(codomain):
                yield Bijection(zip(domain, f))

    @typecheck(Function)
    def __contains__(self, other):
        # Cannot use self.domain == other.domain since Jython cannot
        # compare sets and key_views for some reason (sigh...)
        if not self.domain.symmetric_difference(other.domain):
            if self.invertible:
                return self.codomain == other.image()
            else:
                return self.codomain.issuperset(other.image())
        return False

    def __len__(self):
        if self.invertible:
            return factorial(len(self.domain))
        else:
            return len(self.codomain) ** len(self.domain)


Isomorphisms = partial(Mappings, invertible=True)
TransformationMonoid = partial(Mappings, codomain=None, invertible=False)
SymmetricGroup = partial(Mappings, codomain=None, invertible=True)
