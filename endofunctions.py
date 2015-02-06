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
        self.func = tuple(func)
        self.n = len(self.func)
        self._preim = None

    def __hash__(self):
        return hash(self.func)

    def __len__(self):
        return self.n

    def __repr__(self):
        return self.__class__.__name__+'('+str(list(self.func))+')'

    def __str__(self):
        funcstring = self.__class__.__name__+'(['
        mapvals = []
        for x, f in enumerate(self.func[:-1]):
            mapvals.append(str(x)+'->'+str(f)+', ')
        funcstring += ''.join(mapvals)
        funcstring += str(self.n-1)+"->"+str(self.func[-1])+'])'
        return funcstring

    def __iter__(self):
        return iter(self.func)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.func == other.func
        return False

    def __ne__(self, other):
        return not self == other

    def compose(self, other):
        """If f(x)=self and g(x)=other return f(g(x))."""
        return self.__class__(self.func[x] for x in other)

    def iterate(self, n):
        """
        Efficiently iterate by self-composing, inspired by exponentiation by
        squaring.
        """
        # Convert to string of binary digits, clip off 0b, then reverse.
        component_iterates = bin(n)[2::][::-1]
        f = self
        f_iter = self.__class__(range(self.n))
        for it in component_iterates:
            if it == '1':
                f_iter = f_iter.compose(f)
            f = f.compose(f)
        return f_iter

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
            self._preim = [set() for _ in range(self.n)]
            for x in range(self.n):
                self._preim[self.func[x]].add(x)
        return self._preim


f = Endofunction([0,0,1,2,3,4,5,6,7,8,9])
g1 = f.iterate(2)
print f
print g1
print f.preim()
print g1.preim()
print f.preim2()
print g1.preim2()
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
    