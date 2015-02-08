#!/usr/bin/env python
# Copyright (C) 2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.

import random
import unittest
import itertools
import productrange

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
        """Iterate by self-composing, inspired by exponentiation by squaring."""
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
        algorithm should take O(len(self.domain)) time.
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
        return set(tuple(cycle) for cycle in self._enumerate_cycles())

    @property
    def cycles(self):
        if self._cycles is None:
            self._cycles = self._calculate_cycles()
        return self._cycles

    @property
    def limitset(self):
        if self._limitset is None:
            self._limitset = set(itertools.chain.from_iterable(self.cycles))
        return self._limitset

    def _calculate_attached_treenodes(self):
        """
        Returns subsets of the preimages of each element which are not in
        cycles.
        """
        descendants = [set() for _ in range(self._n)]
        for x, inv_image in enumerate(self.preimage):
            for f in inv_image:
                if f not in self.limitset:
                    descendants[x].add(f)
        return descendants

    @property
    def attached_treenodes(self):
        if self._descendants is None:
            self._descendants = self._calculate_attached_treenodes()
        return self._descendants

    def attached_level_sequence(self, node, level=1):
        """
        Given an element of self's domain, return a level sequence of the
        rooted tree formed from the graph of all noncyclic nodes whose paths
        iteration paths pass through node.

        At each call it builds the level sequence with first element at the
        current level and appends the level sequences of the attached subtrees
        of each noncyclic element in the preimage the the node, with the
        subtrees' level sequences starting one level higher than the current
        node.
        """
        level_sequence = [level]
        for x in self.attached_treenodes[node]:
            level_sequence += self.attached_level_sequence(x, level+1)
        return level_sequence

    @classmethod
    def randfunc(cls, n):
        return cls(random.randrange(n) for I in range(n))


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


class EndofunctionTests(unittest.TestCase):

    def test_iterate(self):
        sigma = Endofunction([1, 2 ,3, 0, 5, 6, 4]) # Perm (0,1,2,3)(4,5,6)
        identity = Endofunction(range(7)).cycles
        for I in range(1, 11): # Order of cycle is 12
            self.assertNotEqual(identity, sigma.iterate(I).cycles)
        self.assertItemsEqual(identity, sigma.iterate(12).cycles)

    def test_imagepath(self):
        """Check various special and degenerate cases, with right index"""
        self.assertEqual([1], Endofunction([0]).imagepath)
        self.assertEqual([1], Endofunction([0, 0]).imagepath)
        self.assertEqual([1], Endofunction([1, 1]).imagepath)
        self.assertEqual([2], Endofunction([0, 1]).imagepath)
        self.assertEqual([2], Endofunction([1, 0]).imagepath)
        node_count = [2, 3, 5, 15]
        for n in node_count:
            tower = Endofunction([0] + list(range(n-1)))
            cycle = Endofunction([n-1] + list(range(n-1)))
            fixed = Endofunction(list(range(n)))
            degen = Endofunction([0]*n)
            self.assertEqual(list(range(n)[:0:-1]), tower.imagepath)
            self.assertEqual([n]*(n-1), cycle.imagepath)
            self.assertEqual([n]*(n-1), fixed.imagepath)
            self.assertEqual([1]*(n-1), degen.imagepath)

    # Cycle tests
    funcs = [
        [1, 0],
        [9, 5, 7, 6, 2, 0, 9, 5, 7, 6, 2],
        [7, 2, 2, 3, 4, 3, 9, 2, 2, 10, 10, 11, 12, 5]
    ]
    # Use magic number for python3 compatibility
    funcs += list([Endofunction.randfunc(20) for I in range(100)])
    funcs += list(productrange.endofunctions(1))
    funcs += list(productrange.endofunctions(3))
    funcs += list(productrange.endofunctions(4))
    funcs = list(map(Endofunction, funcs))

    def test_cycles_are_cyclic(self):
        """Make sure funccylces actually returns cycles."""
        for f in self.funcs:
            for cycle in f.cycles:
                for ind, el in enumerate(cycle):
                    self.assertEqual(cycle[(ind+1) % len(cycle)], f[el])

    def test_cycles_are_unique(self):
        """Ensure funccycles returns no duplicates."""
        for f in self.funcs:
            self.assertEqual(len(f.cycles), len(set(f.cycles)))

    def test_cycles_are_complete(self):
        """Ensure funccycles returns every cycle."""
        for f in self.funcs:
            self.assertEqual(f.imagepath[-1], len(f.limitset))

    def test_attached_treenodes_are_not_cyclic(self):
        """Make sure attached_treenodes returns nodes not in cycles.."""
        for f in self.funcs:
            lim = f.limitset
            descendents = f.attached_treenodes
            for preim in descendents:
                for x in preim:
                    self.assertTrue(x not in lim)

if __name__ == '__main__':
    unittest.main()

    