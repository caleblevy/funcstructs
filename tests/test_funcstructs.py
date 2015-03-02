#!/usr/bin/env python
# Copyright (C) 2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.

import unittest

from endofunction_structures.funcstructs import *


class FuncstructTests(unittest.TestCase):

    def test_func_form(self):
        """Convert struct to func and back, and check we get the same thing."""
        struct = Funcstruct([
            necklaces.Necklace([
                rootedtrees.DominantTree([1, 2, 3]),
                rootedtrees.DominantTree([1, 2, 2])
            ]),
            necklaces.Necklace([
                rootedtrees.DominantTree([1, 2])
            ]),
            necklaces.Necklace([
                rootedtrees.DominantTree([1, 2, 2]),
                rootedtrees.DominantTree([1]),
                rootedtrees.DominantTree([1, 2, 2])
            ])
        ])
        self.assertEqual(struct, Funcstruct(struct.func_form()))

    def test_imagepath(self):
        """Check methods for computing structure image paths are equivalent."""
        for i in range(1, 8):
            for struct in EndofunctionStructures(i):
                sim = endofunctions.Endofunction(struct.func_form()).imagepath
                fim = struct.imagepath
                np.testing.assert_array_equal(sim, fim)

    def test_struct_counts(self):
        """OEIS A001372: Number of self-mapping patterns."""
        A001372 = [1, 3, 7, 19, 47, 130, 343, 951, 2615, 7318, 20491, 57903]
        for i, count in enumerate(A001372):
            s = set()
            s.update(EndofunctionStructures(i+1))
            s.update(partition_funcstructs(i+1))
            self.assertEqual(count, len(s))
            self.assertEqual(count, EndofunctionStructures(i+1).cardinality())

    def test_degeneracy(self):
        """OEIS A000312: Number of labeled maps from n points to themselves."""
        for i in range(1, 8):
            fac = counts.factorial(i)
            func_count = 0
            for struct in EndofunctionStructures(i):
                func_count += fac//struct.degeneracy
            self.assertEqual(i**i, func_count)

    def test_partition_order_unimportant(self):
        """Test for equivalence of Funcstruct representations."""
        self.assertEqual(
            EndofunctionStructures(10, [3, 3, 2]),
            EndofunctionStructures(10, [2, 3, 3])
        )
        self.assertNotEqual(
            EndofunctionStructures(10),
            EndofunctionStructures(10, [2, 2, 3])
        )
        self.assertNotEqual(
            EndofunctionStructures(11, [3, 3, 3]),
            EndofunctionStructures(10, [3, 3, 3])
        )

    def test_repr(self):

        from endofunction_structures.necklaces import Necklace
        from endofunction_structures.rootedtrees import DominantTree

        struct = Funcstruct(endofunctions.randfunc(30))
        self.assertEqual(struct, eval(repr(struct)))
        node_counts = [3, 5, 10, 50]
        for n in node_counts:
            structs = EndofunctionStructures(n)
            self.assertEqual(structs, eval(repr(structs)))
        s = EndofunctionStructures([10, [2, 2, 3]])
        self.assertEqual(s, eval(repr(s)))

    def test_keyability(self):
        dic = {}
        a = EndofunctionStructures(10)
        dic[a] = 1
        dic[EndofunctionStructures(10, [10])] = 2
        self.assertEqual(len(dic), 2)
        dic[EndofunctionStructures(10)] += 1
        self.assertEqual(len(dic), 2)
