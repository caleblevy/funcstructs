# Copyright (C) 2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.

""" Data structures for representing endofunction structures: mappings from a
finite set into itself. """

import random

import numpy as np
from memoized_property import memoized_property

from . import productrange
from . import rootedtrees


class Endofunction(object):
    """Implementation of an endofunction as a map of range(N) into itself using
    a list."""

    def __init__(self, func):
        if isinstance(func, rootedtrees.LevelTree):
            func = func.labelled_sequence()
        self.func = tuple(func)

    def __hash__(self):
        return hash(self.func)

    def __len__(self):
        """len(f) is the number of elements in f's domain"""
        return len(self.func)

    def __repr__(self):
        return type(self).__name__+'(%s)'+str(list(self))

    def __str__(self):
        funcstring = type(self).__name__+'(['
        mapvals = []
        for x, f in enumerate(self[:-1]):
            mapvals.append(str(x)+'->'+str(f)+', ')
        funcstring += ''.join(mapvals)
        funcstring += str(len(self)-1)+"->"+str(self[-1])+'])'
        return funcstring

    def __getitem__(self, x):
        """f(x) <==> f[x]"""
        return self.func[x]

    def __iter__(self):
        """[f(x) for x in range(len(f))] <==> list(iter(self))"""
        return iter(self.func)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.func == other.func
        return False

    def __ne__(self, other):
        return not self == other

    def __call__(self, other):
        """f(g) <==> Endofunction(f[g[x]] for x in g.domain)"""
        return Endofunction([self[x] for x in other])

    @memoized_property
    def domain(self):
        return frozenset(range(len(self)))

    @memoized_property
    def image(self):
        return frozenset(self)

    @memoized_property
    def preimage(self):
        """f.preimage[y] <==> {x for x in f.domain if f[x] == y}"""
        preim = [set() for _ in range(len(self))]
        for x in self.domain:
            preim[self[x]].add(x)
        return tuple(map(frozenset, preim))

    @memoized_property
    def imagepath(self):
        """f.imagepath[n] <==> len(set(f**n)) for n in range(1, len(f))"""
        cardinalities = [len(self.image)]
        f = self
        card_prev = len(self)
        for it in range(1, len(self)-1):
            f = f(self)
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
                f_iter = f_iter(f)
            f = f(f)
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

    @memoized_property
    def cycles(self):
        """Return the set of f's cycles"""
        return frozenset(tuple(cycle) for cycle in self.enumerate_cycles())

    @memoized_property
    def limitset(self):
        """x in f.limitset <==> any(x in cycle for cycle in f.cycles)"""
        return frozenset(productrange.flatten(self.cycles))

    @memoized_property
    def attached_treenodes(self):
        """f.attached_treenodes[y] <==> f.preimage[y] - f.limitset"""
        descendants = [set() for _ in range(len(self))]
        for x, inv_image in enumerate(self.preimage):
            for f in inv_image:
                if f not in self.limitset:
                    descendants[x].add(f)
        return tuple(map(frozenset, descendants))

    def _attached_level_sequence(self, node, level=1):
        """Return the level sequence of the rooted tree formed from the graph
        of all noncyclic nodes whose iteration paths pass through node"""
        level_sequence = [level]
        for x in self.attached_treenodes[node]:
            level_sequence.extend(self._attached_level_sequence(x, level+1))
        return level_sequence

    def attached_tree(self, node):
        return rootedtrees.DominantTree(self._attached_level_sequence(node))

    def tree_form(self):
        """Test if a function has a tree structure and if so return it"""
        cycles = list(self.cycles)
        if len(cycles) != 1 or len(cycles[0]) != 1:
            raise ValueError("Function structure is not a rooted tree")
        root = cycles[0][0]
        return rootedtrees.DominantTree(self.attached_tree(root))

    def randconj(self):
        """Return a random conjugate of f."""
        return randperm(len(self)).conj(self)


def randfunc(n):
    """ Return a random endofunction on n elements. """
    return Endofunction([random.randrange(n) for I in range(n)])


def cycles_to_funclist(cycles):
    """Convert cycle decomposition into endofunction"""
    funclist = [0] * len(productrange.flatten(cycles))
    for cycle in cycles:
        for i, el in enumerate(cycle[:-1]):
            funclist[el] = cycle[i+1]
        funclist[cycle[-1]] = cycle[0]
    return funclist


class SymmetricFunction(Endofunction):
    """ An invertible endofunction. """

    def __init__(self, func):
        func = tuple(func)
        if hasattr(func, '__getitem__') and hasattr(func[0], '__iter__'):
            # If it is a cycle decomposition, change to function.
            func = cycles_to_funclist(func)
        super(SymmetricFunction, self).__init__(func)
        if not len(self) == len(self.image):
            raise ValueError("This function is not invertible.")

    def __pow__(self, n):
        """Symmetric functions allow us to take inverses."""
        if n >= 0:
            return Endofunction.__pow__(self, n)
        else:
            return Endofunction.__pow__(self.inverse, -n)

    def __mul__(self, other):
        """Multiply notation for symmetric group."""
        return SymmetricFunction(self(other))

    @memoized_property
    def inverse(self):
        """ Returns the inverse of a permutation of range(n). Code taken
        directly from: "Inverting permutations in Python" at
        http://stackoverflow.com/a/9185908. """
        inv = [0] * len(self)
        for i, p in enumerate(self):
            inv[p] = i
        return self.__class__(inv)

    def conj(self, func):
        """Conjugate a function f by a permutation."""
        return self.inverse(func)(self)


def randperm(n):
    """Returns a random permutation of range(n)."""
    r = list(range(n))  # Explicitly call ist for python 3 compatibility.
    random.shuffle(r)
    return SymmetricFunction(r)


class TransformationMonoid(object):
    """Set of all endofunctions on n elements."""

    def __init__(self, set_size):
        if set_size < 1:
            raise ValueError("Set must have at least one element.")
        self.n = set_size

    def __hash__(self):
        return hash(self.n)

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.n == other.n
        return False

    def __ne__(self, other):
        return not self == other

    __lt__ = None

    def __iter__(self):
        for func in productrange.productrange([self.n] * self.n):
            yield Endofunction(func)

    def __len__(self):
        return self.n ** self.n

    def __contains__(self, other):
        if isinstance(other, Endofunction):
            return self.n == other._n
        return False

    def __repr__(self):
        return self.__class__.__name__+'('+str(self.n)+')'

    def iterdist(self):
        """ Calculate iterdist by enumerating all endofunction image paths."""
        M = np.zeros((self.n, self.n-1), dtype=object)
        for f in self:
            im = f.imagepath
            for it, card in enumerate(im):
                M[card-1, it] += 1
        return M
