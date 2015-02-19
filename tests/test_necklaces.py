#!/usr/bin/env python
# Copyright (C) 2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.

import unittest

from endofunction_structures.necklaces import *


class PeriodicityTest(unittest.TestCase):

    def test_periodicities(self):
        """Test periodicities of various lists"""
        periods = []
        lists = []
        N = 20
        for n in range(1, N+1):
            for d in factorization.divisors(n):
                periods.append(d)
                lists.append(([0]+[1]*(d-1))*(n//d))

        t1 = [(1, 2), ]*3+[(1, 1)]
        t2 = t1*3 + [(1, 4, 3)]*3 + [(1, )]
        t3 = t2*2 + [(2, )]*3 + [(1, 4, 3)]
        t4 = t3*3 + [(3, )]*3+[(1, 2)]
        lists.append(t4*4)
        periods.append(112)

        lists.extend([[(1, 2), (1, 2)], 
                      [(1, 2), (1, )],
                      [(1, 2), (1, ), (1, 2), (1, ), (1, )],
                      [(1, 2), (1, ), (1, 2), (1, ), (1, 2)]])
        periods.extend([1, 2, 5, 5])

        for period, lst in zip(periods, lists):
            self.assertEqual(period, periodicity(lst))


class NecklaceTests(unittest.TestCase):

    def test_equality(self):
        """Make sure rotationally equivalent necklaces compare equal."""
        n = Necklace([1, 2, 3, 1, 2, 3])
        nshort = Necklace([1, 2, 3])
        nlong = Necklace([1, 2, 3, 1, 2, 3, 1, 2, 3])
        nrot = Necklace([3, 1, 2, 3, 1, 2])
        ntype = Necklace(tuple([2, 3, 1, 2, 3, 1]))

        self.assertNotEqual(n, nshort)
        self.assertNotEqual(n, nlong)
        self.assertEqual(n, nrot)
        self.assertEqual(n, ntype)

    def test_containement(self):
        """Make sure Necklace conjugacy class contains all its rotations."""
        n = Necklace([1, 2, 3, 1, 2, 3])
        self.assertFalse(n in n)
        self.assertTrue(tuple([3, 1, 2, 3, 1, 2]) in n)

    def test_hash(self):
        """Test that our hash is rotationally invariant."""
        self.assertEqual(hash(Necklace([1, 2, 3])), hash(Necklace([3, 1, 2])))

    def test_repr(self):
        n = Necklace([1, 2, 3, 1, 2, 3])
        self.assertTrue(n == eval(repr(n)))

    def test_necklace_as_key(self):
        dic = {}
        neck = Necklace([1, 2, 3, 1, 2, 3])
        dic[neck] = 1
        dic[neck] += 1
        self.assertEqual(1, len(dic))
        self.assertEqual(dic[neck], 2)

        neck2 = Necklace([3, 1, 2, 3, 1, 2])
        dic[neck2] += 1
        self.assertEqual(dic[neck], 3)
        self.assertEqual(1, len(dic))

        neck3 = Necklace([3, 2, 1, 3, 2, 1])
        with self.assertRaises(KeyError):
            dic[neck3] += 1

        dic[neck3] = 7
        self.assertEqual(2, len(dic))


class NecklaceEnumerationTests(unittest.TestCase):

    def test_counts(self):
        """Verify the count_by_period method correctly counts necklaces."""
        cp1 = [1]*3 + [2]*3 + [3]*2
        cp2 = [1]*4 + [2]*4 + [3]*4 + [4]*3 + [5]*3 + [6]*2 + [7] + [8]
        cp3 = [1]*24 + [2]*36
        # color_partitions = [[3, 3, 2], [4, 4, 4, 3, 3, 2, 1, 1], [24, 36]]
        color_partitions = [cp1, cp2, cp3]
        color_cardinalities = [70, 51330759480000, 600873126148801]
        for cp, cc in zip(color_partitions, color_cardinalities):
            self.assertEqual(cc, len(NecklaceGroup(cp)))

    def test_enumeration(self):
        """Test necklace counts for various bead sets."""
        beadsets = [[4, 4, 5, 5, 2, 2, 2, 2, 2, 2, 6, 6],
                    [4, 4, 5, 5, 2, 2, 2, 2, 2, 2, 6, 6, 6], [0]]
        for beadset in beadsets:
            count = 0
            necklaces = set()
            for necklace in NecklaceGroup(beadset):
                count += 1
                necklaces.add(necklace)
                necklaces.add(necklace)
            self.assertEqual(len(necklaces), count)