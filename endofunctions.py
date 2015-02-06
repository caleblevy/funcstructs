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
        """Iteration by self-composing, inspired by exponentiation by squaring."""
        # Convert to string of binary digits, clip off 0b, then reverse.
        component_iterates = bin(n)[2::][::-1]
        f = self
        f_iter = self.__class__(range(self.n))
        for it in component_iterates:
            if it == '1':
                f_iter = f_iter.compose(f)
            f = f.compose(f)
        return f_iter

    def imagepath(self):
        cardinalities = [len(set(f))]
        f_iter = self
        card_prev = self.n
        for it in range(1, self.n-1):
            f_iter = f_iter.compose(self)
            card = let(set(f_iter))

f = Endofunction([0,0,1,2,3,4,5,6,7,8,9])
g1 = f.iterate(2)
print f
print g1

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
    