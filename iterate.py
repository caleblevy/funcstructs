#!/usr/bin/env python
# Copyright (C) 2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.


"""
A collection of utilities returning certain information about and kinds of
images of sets under functions: preimages, cardinalities of iterate images,
cycle decompositions and limitsets.

These should all be made into methods. We will have:
    - f.cycles()
    - f.preimage(I)
"""

import random
import unittest

import nestops
import productrange


randfunc = lambda n: [random.randrange(n) for I in range(n)]


def compose(f, g):
    """Takes two endofunctions f, g and returns f(g(x))."""
    return [f[x] for x in g]


def iter2(f):
    """Compose f with itself"""
    return compose(f, f)


def iterate(f, n):
    """Iteration by self-composing, inspired by exponentiation by squaring."""
    # Convert to string of binary digits, clip off 0b, then reverse.
    component_iterates = bin(n)[2::][::-1]
    f_iter = range(len(f))
    for it in component_iterates:
        if it == '1':
            f_iter = compose(f_iter, f)
        f = iter2(f)
    return f_iter


def imagepath(f):
    """
    Give it a list such that all([I in range(len(f)) for I in f]) and this
    program spits out the image path of f.
    """
    n = len(f)
    cardinalities = [len(set(f))]
    f_iter = f[:]
    card_prev = n
    for it in range(1, n-1):
        f_iter = compose(f_iter, f)
        card = len(set(f_iter))
        cardinalities.append(card)
        # Save some time; if we have reached the fixed set, return.
        if card == card_prev:
            cardinalities.extend([card]*(n-2-it))
            break
        card_prev = card
    return cardinalities


def preimage(f):
    """
    Given an endofunction f defined on S=range(len(f)), returns the preimage of
    f. If g=preimage(f), we have

        g[y]=[x for x in S if f[x]==y],

    or mathematically:

        f^-1(y)={x in S: f(x)=y}.

    Note the particularly close correspondence between python's list
    comprehensions and mathematical set-builder notation.
    """
    S = range(len(f))
    preim = []
    for y in S:
        preim.append([x for x in S if y == f[x]])
    return preim


def funccycles(f):
    """
    Returns the cycle decomposition of an endofunction f. Should take O(len(f))
    time.
    """
    n = len(f)
    if n == 1:
        yield [0]
        return
    # If we run  elements for total of O(len(f)) time.
    prev_els = set()
    for x in range(n):
        skip_el = False
        path = [x]
        path_els = set(path)
        for it in range(n+1):
            x = f[x]
            path.append(x)
            # If we hit an element seen in a previous path, this path will not
            # contain a new cycle.
            if x in prev_els:
                skip_el = True
                break
            # If an element appears in the path twice, we have already found
            # the cycle
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


limitset = lambda f: nestops.flatten(funccycles(f))


def attached_treenodes(f):
    """
    Returns subsets of the preimages of each element which are not in cycles.
    """
    descendents = preimage(f)
    limset = limitset(f)
    for preim in descendents:
        for x in limset:
            if x in preim:
                preim.remove(x)
    return descendents


class ImagepathTest(unittest.TestCase):

    def testImagepath(self):
        """Check various special and degenerate cases, with right index"""
        self.assertEqual([1], imagepath([0]))
        self.assertEqual([1], imagepath([0, 0]))
        self.assertEqual([1], imagepath([1, 1]))
        self.assertEqual([2], imagepath([0, 1]))
        self.assertEqual([2], imagepath([1, 0]))
        node_count = [2, 3, 5, 15]
        for n in node_count:
            tower = [0] + list(range(n-1))
            cycle = [n-1] + list(range(n-1))
            fixed = list(range(n))
            degen = [0]*n
            self.assertEqual(list(range(n)[:0:-1]), imagepath(tower))
            self.assertEqual([n]*(n-1), imagepath(cycle))
            self.assertEqual([n]*(n-1), imagepath(fixed))
            self.assertEqual([1]*(n-1), imagepath(degen))


class CycleTests(unittest.TestCase):
    funcs = [
        [1, 0],
        [9, 5, 7, 6, 2, 0, 9, 5, 7, 6, 2],
        [7, 2, 2, 3, 4, 3, 9, 2, 2, 10, 10, 11, 12, 5]
    ]
    # Use magic number for python3 compatibility
    funcs += list([randfunc(20) for I in range(100)])
    funcs += list(productrange.endofunctions(1))
    funcs += list(productrange.endofunctions(3))
    funcs += list(productrange.endofunctions(4))

    def testCyclesAreCyclic(self):
        """Make sure funccylces actually returns cycles."""
        for f in self.funcs:
            for cycle in funccycles(f):
                for ind, el in enumerate(cycle):
                    self.assertEqual(cycle[(ind+1) % len(cycle)], f[el])

    def testCyclesAreUnique(self):
        """Ensure funccycles returns no duplicates."""
        for f in self.funcs:
            cycleset = [tuple(cycle) for cycle in funccycles(f)]
            self.assertEqual(len(cycleset), len(set(cycleset)))

    def testCyclesAreComplete(self):
        """Ensure funccycles returns every cycle."""
        for f in self.funcs:
            cycle_size = len(nestops.flatten(funccycles(f)))
            self.assertEqual(imagepath(f)[-1], cycle_size)

    def testTreenodesAreNotCyclic(self):
        """Make sure attached_treenodes returns nodes not in cycles.."""
        for f in self.funcs:
            lim = limitset(f)
            descendents = attached_treenodes(f)
            for preim in descendents:
                for x in preim:
                    self.assertTrue(x not in lim)


if __name__ == '__main__':
    unittest.main()
