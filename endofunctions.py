#!/usr/bin/env python
# Copyright (C) 2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.
import random
import unittest
import itertools

class Endofunction(object):
    """
    Implementation of an endofunction object: a map from set(range(N)) to
    itself.
    """
    def __init__(self, func):
        self._func = tuple(func)
        self._n = len(self._func)
        """
        The following are implemented as properties of the function; these are
        not things you 'do' to the endofunction; these are properties that they
        have.
        """
        self._preim = None
        self._cycles = None
        self._limitset = None
        self._descendants = None

    def __hash__(self):
        return hash(self._func)

    def __repr__(self):
        return self.__class__.__name__+'('+str(list(self._func))+')'

    def __str__(self):
        funcstring = self.__class__.__name__+'(['
        mapvals = []
        for x, f in enumerate(self._func[:-1]):
            mapvals.append(str(x)+'->'+str(f)+', ')
        funcstring += ''.join(mapvals)
        funcstring += str(self._n-1)+"->"+str(self._func[-1])+'])'
        return funcstring

    def __getitem__(self, ind):
        return self._func[ind]

    def __iter__(self):
        return iter(self._func)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._func == other._func
        return False

    def __ne__(self, other):
        return not self == other

    def __call__(self, other):
        """If f(x)=self and g(x)=other return f(g(x))."""
        return self.__class__(self[x] for x in other)

    @property
    def domain(self):
        return set(range(self._n))

    @property
    def imageset(self):
        """Return all elements in the image of self."""
        return set(self._func)

    def _calculate_preimage(self):
        """
        Given an endofunction f defined on S=range(len(f)), returns the
        preimage of f. If g=preimage(f), we have

            g[y]=[x for x in S if f[x]==y],

        or mathematically:

            f^-1(y)={x in S: f(x)=y}.

        Note the particularly close correspondence between python's list
        comprehensions and mathematical set-builder notation.
        """
        preim = [set() for _ in range(self._n)]
        for x in range(self._n):
            preim[self._func[x]].add(x)
        return preim

    @property
    def preimage(self):
        if self._preim is None:
            self._preim = self._calculate_preimage()
        return self._preim

    @property
    def imagepath(self):
        """
        Give it a list such that all([I in range(len(f)) for I in f]) and this
        program spits out the image path of f.
        """
        cardinalities = [len(self.imageset)]
        f = self
        card_prev = self._n
        for it in range(1, self._n-1):
            f = f(self)
            card = len(f.imageset)
            cardinalities.append(card)
            # Save some time; if we have reached the fixed set, return.
            if card == card_prev:
                cardinalities.extend([card]*(self._n-2-it))
                break
            card_prev = card
        return cardinalities

    def iterate(self, n):
        """
        Efficiently iterate by self-composing, inspired by exponentiation by
        squaring.
        """
        # Convert to string of binary digits, clip off 0b, then reverse.
        component_iterates = bin(n)[2::][::-1]
        f = self
        f_iter = self.__class__(range(self._n))
        for it in component_iterates:
            if it == '1':
                f_iter = f_iter(f)
            f = f(f)
        return f_iter

    def _enumerate_cycles(self):
        """
        Returns self's cycle decomposition. Since lookup in sets is O(1), this
        algorithm should take O(self._n) time.
        """
        if self._n == 1:
            yield [0]
            return
        # If we run  elements for total of O(len(f)) time.
        prev_els = set()
        for x in range(self._n):
            skip_el = False
            path = [x]
            path_els = set(path)
            for it in range(self._n+1):
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

    def _calculate_cycles(self):
        return list(tuple(cycle) for cycle in self._enumerate_cycles())

    @property
    def cycles(self):
        if self._cycles is None:
            self._cycles = self._calculate_cycles()
        return self._cycles

    @property
    def limitset(self):
        if self._limitset is None:
            self._limitset = list(itertoos.chain.from_iter(self.cycles))
        return self._limitset

    def _calculate_attached_nodes(self):
        """
        Returns subsets of the preimages of each element which are not in
        cycles.
        """
        descendants = self.preimage
        for inv_image in descendants:
            for x in inv_image:
                if x in self.limitset:
                    inv_image.remove(x)
        return descendants

    @property
    def attached_nodes(self):
        if self._descendants is None:
            self._descendants = self._calculate_attached_nodes
        return self._descendants

f = Endofunction([1,2,3,0,5,6,4])
print f
print f.cycles
a = f.iterate(3)
print a
print a.cycles
a = f.iterate(4)
print a
print a.cycles
a = f.iterate(12)
print a

print a == f
print a == Endofunction(range(7))
print a._cycles
print a.cycles




class TransformationMonoid(object):
    """Set of all endofunctions."""
    def __iter__(self):
        pass
        # for func in productrange return Endofunction(self)
    def __len__(self):
        pass
        # return n**n
    def __contains__(self, other):
        pass
        # if funccheck return true
    def __le__(self, other):
        pass
        # return self.n < other.n
    