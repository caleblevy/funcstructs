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
        self._preim = None
        self._cycles = None

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

    def preim(self):
        """
        Given an endofunction f defined on S=range(len(f)), returns the
        preimage of f. If g=preimage(f), we have

            g[y]=[x for x in S if f[x]==y],

        or mathematically:

            f^-1(y)={x in S: f(x)=y}.

        Note the particularly close correspondence between python's list
        comprehensions and mathematical set-builder notation.
        """
        if self._preim is None:
            self._preim = [set() for _ in range(self._n)]
            for x in range(self._n):
                self._preim[self[x]].add(x)
        return self._preim

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

    def _compute_cycles(self):
        """
        Returns the cycle decomposition of an endofunction f. Should take O(len(f))
        time.
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

    def cycles(self):
        if self._cycles is None:
            self._cycles = list(tuple(cycle) for cycle in self._compute_cycles())
        return self._cycles

f = Endofunction([1,2,3,0,5,6,4])
print f
print f.cycles()
a = f.iterate(3)
print a
print a.cycles()
a = f.iterate(4)
print a
print a.cycles()
a = f.iterate(12)
print a

print a == f
print a == Endofunction(range(7))
print a._cycles
print a.cycles()




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
    