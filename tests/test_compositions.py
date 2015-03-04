#!/usr/bin/env python
# Copyright (C) 2014-2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.

import unittest

from endofunction_structures.compositions import *
from endofunction_structures import counts


class CompositionTests(unittest.TestCase):

    def test_composition_counts(self):
        """Ensure #(compositions(n)) = 2^(n-1)"""
        n = 10
        for i in range(1, n):
            self.assertEqual(2**(i-1), len(list(compositions(i))))

    def test_composition_sums(self):
        """Check that compositions of n sum to n"""
        n = 10
        for i in range(1, n):
            for comp in compositions(i):
                self.assertEqual(i, sum(comp))

    def test_weak_composition_counts(self):
        """Ensure there are nCk(n, k) weak compositions of n into k parts."""
        for n in range(1, 5):
            for k in range(1, 10):
                l = list(weak_compositions(n, k))
                self.assertEqual(counts.nCk(n+k-1, k-1), len(l))

    def test_weak_composition_sums(self):
        """Ensure each weak composition sums to n"""
        for n in range(1, 5):
            for k in range(1, 10):
                for comp in weak_compositions(n, k):
                    self.assertEqual(n, sum(comp))
