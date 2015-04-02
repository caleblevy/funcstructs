# Copyright (C) 2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.

import unittest

from endofunction_structures.endofunctions import *
from endofunction_structures.rootedtrees import OrderedTree


class EndofunctionTests(unittest.TestCase):

    # Imagepath Tests

    def test_iterate(self):
        sigma = Endofunction([1, 2, 3, 0, 5, 6, 4])  # Perm (0,1,2,3)(4,5,6)
        identity = Endofunction(range(7))
        for I in range(1, 11):  # Order of cycle is 12
            self.assertNotEqual(identity.cycles, (sigma**I).cycles)
        self.assertEqual(identity.cycles, (sigma**12).cycles)

    def test_imagepath(self):
        """Check various special and degenerate cases, with right index"""
        self.assertSequenceEqual([1], Endofunction([0]).imagepath)
        self.assertSequenceEqual([1], Endofunction([0, 0]).imagepath)
        self.assertSequenceEqual([1], Endofunction([1, 1]).imagepath)
        self.assertSequenceEqual([2], Endofunction([0, 1]).imagepath)
        self.assertSequenceEqual([2], Endofunction([1, 0]).imagepath)
        node_count = [2, 3, 5, 15]
        for n in node_count:
            tower = Endofunction([0] + list(range(n-1)))
            cycle = Endofunction([n-1] + list(range(n-1)))
            fixed = Endofunction(list(range(n)))
            degen = Endofunction([0]*n)
            self.assertSequenceEqual(list(range(n)[:0:-1]), tower.imagepath)
            self.assertSequenceEqual([n]*(n-1), cycle.imagepath)
            self.assertSequenceEqual([n]*(n-1), fixed.imagepath)
            self.assertSequenceEqual([1]*(n-1), degen.imagepath)

    # Cycle tests

    funcs = [
        Endofunction([1, 0]),
        Endofunction([9, 5, 7, 6, 2, 0, 9, 5, 7, 6, 2]),
        Endofunction([7, 2, 2, 3, 4, 3, 9, 2, 2, 10, 10, 11, 12, 5])
    ]
    funcs += list([randfunc(20) for _ in range(100)])
    funcs += list(TransformationMonoid(1))
    funcs += list(TransformationMonoid(3))
    funcs += list(TransformationMonoid(4))

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
                    self.assertNotIn(x, lim)

    # Permutation Tests

    def test_inverse(self):
        """Test compose(inv(perm), perm) == perm"""
        permlist = []
        for n in range(1, 10):
            for _ in range(1, 10*n):
                permlist.append(randperm(n))

        for perm in permlist:
            e = SymmetricFunction(range(len(perm)))
            self.assertEqual(e, perm * perm.inverse)
            self.assertEqual(e, perm.inverse * perm)
            self.assertEqual(perm, perm.inverse.inverse)

    def test_conjugation(self):
        """Test that conjugation is invertible, with the obvious inverse."""
        for f in self.funcs:
            for _ in range(20):
                perm = randperm(len(f))
                self.assertEqual(f, perm.inverse.conj(perm.conj(f)))

    def test_from_tree(self):
        """Make sure Endofunction finds a correct representative for a given
        tree"""
        tree = OrderedTree([1, 2, 3, 4, 4, 4, 3, 4, 4, 2, 3, 3, 2, 3])
        func = Endofunction([0, 0, 1, 2, 2, 2, 1, 6, 6, 0, 9, 9, 0, 12])
        self.assertEqual(func, Endofunction(tree))
        with self.assertRaises(ValueError):
            sym = SymmetricFunction(OrderedTree([0]+list(range(5))))

    def test_keyability(self):
        dic = {}
        a = Endofunction(range(10))
        b = Endofunction([0, 0]+list(range(8)))
        dic[a] = 1
        dic[Endofunction(range(10))] += 1
        self.assertEqual(len(dic), 1)
        dic[b] = 2
        self.assertEqual(len(dic), 2)
        c = SymmetricFunction(range(10))
        dic[c] = 7
        self.assertEqual(len(dic), 3)
        dic[c.inverse] = 2
        self.assertEqual(len(dic), 3)
        self.assertEqual(dic[c], 2)
        t = TransformationMonoid(7)
        self.assertEqual(1, len(set([t, t, TransformationMonoid(7)])))
