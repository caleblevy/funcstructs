#!/usr/bin/env python
# Copyright (C) 2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.

""" A collection of utilities returning certain information about and kinds of
images of sets under functions: preimages, cardinalities of iterate images,
cycle decompositions and limit sets. """


import random

import numpy as np
from memoized_property import memoized_property

from . import productrange
from . import rootedtrees


class Endofunction(object):
    """ Implementation of an endofunction object: a map from set(range(N)) to
    itself. """

    def __init__(self, func):
        if isinstance(func, rootedtrees.LevelTree):
            func = func.labelled_sequence()
        self.func = tuple(func)

    def __hash__(self):
        return hash(self.func)

    def __len__(self):
        return len(self.func)

    def __repr__(self):
        return self.__class__.__name__+'('+str(list(self.func))+')'

    def __str__(self):
        funcstring = self.__class__.__name__+'(['
        mapvals = []
        for x, f in enumerate(self.func[:-1]):
            mapvals.append(str(x)+'->'+str(f)+', ')
        funcstring += ''.join(mapvals)
        funcstring += str(len(self)-1)+"->"+str(self.func[-1])+'])'
        return funcstring

    def __getitem__(self, ind):
        return self.func[ind]

    def __iter__(self):
        return iter(self.func)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.func == other.func
        return False

    def __ne__(self, other):
        return not self == other

    def __call__(self, other):
        """If f(x)=self and g(x)=other return f(g(x))."""
        return Endofunction([self[x] for x in other])

    @memoized_property
    def domain(self):
        return set(range(len(self)))

    @memoized_property
    def imageset(self):
        """Return all elements in the image of self."""
        return set(self.func)

    @memoized_property
    def preimage(self):
        """ Given an endofunction f defined on S=range(len(f)), returns the
        preimage of f. If g=preimage(f), we have
            g[y]=[x for x in S if f[x]==y],
        or mathematically:
            f^-1(y)={x in S: f(x)=y}.
        Note the particularly close correspondence between python's list
        comprehensions and mathematical set-builder notation. """
        preim = [set() for _ in range(len(self))]
        for x in range(len(self)):
            preim[self[x]].add(x)
        return preim

    @memoized_property
    def imagepath(self):
        """
        Give it a list such that all([I in range(len(f)) for I in f]) and this
        program spits out the image path of f.
        """
        cardinalities = [len(self.imageset)]
        f = self
        card_prev = len(self)
        for it in range(1, len(self)-1):
            f = f(self)
            card = len(f.imageset)
            cardinalities.append(card)
            # Save some time; if we have reached the fixed set, return.
            if card == card_prev:
                cardinalities.extend([card]*(len(self)-2-it))
                break
            card_prev = card
        return cardinalities

    def __pow__(self, n):
        """ Iterate by self-composing, inspired by exponentiation by squaring.
        """
        # Convert to string of binary digits, clip off 0b, then reverse.
        component_iterates = bin(n)[2::][::-1]
        f = self
        f_iter = self.__class__(range(len(self)))
        for it in component_iterates:
            if it == '1':
                f_iter = f_iter(f)
            f = f(f)
        return f_iter

    def enumerate_cycles(self):
        """ Returns self's cycle decomposition. Since lookup in sets is O(1),
        this algorithm should take O(len(self.domain)) time. """

        if len(self) == 1:
            yield [0]
            return
        # If we run  elements for total of O(len(f)) time.
        prev_els = set()
        for x in self.domain:
            skip_el = False
            path = [x]
            path_els = set(path)
            for it in range(len(self)+1):
                x = self[x]
                path.append(x)
                # If we hit an element seen in a previous path, this path will
                # not contain a new cycle.
                if x in prev_els:
                    skip_el = True
                    break
                # If an element appears in the path twice, we have already
                # found the cycle
                if x in path_els:
                    break
                path_els.add(x)
            prev_els.update(path)
            if skip_el:
                continue
            I = len(path)-2
            while I >= 0 and path[I] != path[-1]:
                I -= 1
            yield path[I+1:]

    @memoized_property
    def cycles(self):
        return set(tuple(cycle) for cycle in self.enumerate_cycles())

    @memoized_property
    def limitset(self):
        return set(productrange.flatten(self.cycles))

    @memoized_property
    def attached_treenodes(self):
        """ Returns subsets of the preimages of each element which are not in
        cycles. """
        descendants = [set() for _ in range(len(self))]
        for x, inv_image in enumerate(self.preimage):
            for f in inv_image:
                if f not in self.limitset:
                    descendants[x].add(f)
        return descendants

    def _attached_level_sequence(self, node, level=1):
        """ Given an element of self's domain, return a level sequence of the
        rooted tree formed from the graph of all noncyclic nodes whose paths
        iteration paths pass through node.

        At each call it builds the level sequence with first element at the
        current level and appends the level sequences of the attached subtrees
        of each noncyclic element in the preimage the the node, with the
        subtrees' level sequences starting one level higher than the current
        node. """
        level_sequence = [level]
        for x in self.attached_treenodes[node]:
            level_sequence.extend(self._attached_level_sequence(x, level+1))
        return level_sequence

    def attached_tree(self, node):
        return rootedtrees.DominantTree(self._attached_level_sequence(node))

    def tree_form(self):
        """Test if a function has a tree structure and if so return it."""
        cycles = list(self.cycles)
        if len(cycles) != 1 or len(cycles[0]) != 1:
            raise ValueError("Function structure is not a rooted tree.")
        root = cycles[0][0]
        return rootedtrees.DominantTree(self.attached_tree(root))

    def randconj(self):
        """Return a random conjugate of f."""
        r = randperm(len(self))
        return r.conj(self)


def randfunc(n):
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
    def __init__(self, func):
        func = tuple(func)
        if hasattr(func, '__getitem__') and hasattr(func[0], '__iter__'):
            # If it is a cycle decomposition, change to function.
            func = cycles_to_funclist(func)
        super(SymmetricFunction, self).__init__(func)
        if not len(self) == len(self.imageset):
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
    """Set of all endofunctions."""

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
