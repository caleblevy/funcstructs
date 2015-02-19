#!/usr/bin/env python
# Copyright (C) 2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.

import unittest

from endofunction_structures.funcstructs import *
from endofunction_structures.necklaces import Necklace
from endofunction_structures.rootedtrees import DominantTree


class FuncstructTests(unittest.TestCase):

    def test_func_form(self):
        struct = Funcstruct([
            Necklace([DominantTree([1, 2, 3]), DominantTree([1, 2, 2])]),
            Necklace([DominantTree([1, 2])]),
            Necklace([DominantTree([1, 2, 2]), DominantTree([1]), DominantTree([1, 2, 2])])
        ])
        self.assertEqual(struct, Funcstruct(struct.func_form()))

    def test_imagepath(self):
        """Check methods for computing structure image paths are equivalent."""
        for i in range(8):
            for ms, ps in zip(FuncstructEnumerator(i+1), partition_funcstructs(i+1)):
                mim = endofunctions.Endofunction(ms.func_form()).imagepath
                pim = endofunctions.Endofunction(ps.func_form()).imagepath
                msim = ms.imagepath
                psim = ps.imagepath
                np.testing.assert_array_equal(mim, msim)
                np.testing.assert_array_equal(pim, psim)

    def test_struct_counts(self):
        """OEIS A001372: Number of self-mapping patterns."""
        A001372 = [1, 3, 7, 19, 47, 130, 343, 951, 2615, 7318, 20491, 57903]
        for i, count in enumerate(A001372):
            s = set()
            s.update(FuncstructEnumerator(i+1))
            s.update(partition_funcstructs(i+1))
            self.assertEqual(count, len(s))
            self.assertEqual(count, len(FuncstructEnumerator(i+1)))

    def test_degeneracy(self):
        """OEIS A000312: Number of labeled maps from n points to themselves."""
        for i in range(1, 8):
            fac = math.factorial(i)
            func_mult_count = func_part_count = 0
            for ms, ps in zip(FuncstructEnumerator(i), partition_funcstructs(i)):
                func_mult_count += fac//ms.degeneracy
                func_part_count += fac//ps.degeneracy
            self.assertEqual(i**i, func_mult_count)
            self.assertEqual(i**i, func_part_count)

    def test_repr(self):
        struct = Funcstruct(endofunctions.randfunc(30))
        self.assertEqual(struct, eval(repr(struct)))
        node_counts = [3, 5, 10, 50]
        for n in node_counts:
            structs = FuncstructEnumerator(n)
            self.assertEqual(structs, eval(repr(structs)))

    def test_hash(self):
        pass
        