#!/usr/bin/env python
# Copyright (C) 2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.

import unittest

from endofunction_structures.compositions import *
from endofunction_structures.multiset import nCk


class CompositionTests(unittest.TestCase):

    def test_counts(self):
        """Ensure #(compositions(n)) = 2^(n-1)"""
        n = 10
        for i in range(1, n):
            self.assertEqual(2**(i-1), len(list(compositions_simple(i))))
            self.assertEqual(2**(i-1), len(list(compositions_binary(i))))

    def test_sums(self):
        """Check that compositions of n sum to n"""
        n = 10
        for i in range(1, n):
            for comp in compositions_simple(i):
                self.assertEqual(i, sum(comp))
            for comp in compositions_binary(i):
                self.assertEqual(i, sum(comp))

    def test_weak_compositions(self):
        """Ensure there are nCk(n, k) weak compositions of n into k parts."""
        for n in range(1, 5):
            for k in range(1, 10):
                self.assertEqual(nCk(n+k-1, k-1), len(list(weak_compositions(n,k))))