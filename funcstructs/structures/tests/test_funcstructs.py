import unittest
from math import factorial

import numpy as np

from .. import endofunctions, necklaces, rootedtrees

from .._funcstructs import Funcstruct, EndofunctionStructures


class FuncstructTests(unittest.TestCase):

    def test_func_form(self):
        """Convert struct to func and back, and check we get the same thing."""
        struct = Funcstruct([
            necklaces.Necklace([
                rootedtrees.DominantTree([0, 1, 2]),
                rootedtrees.DominantTree([0, 1, 1])
            ]),
            necklaces.Necklace([
                rootedtrees.DominantTree([0, 1])
            ]),
            necklaces.Necklace([
                rootedtrees.DominantTree([0, 1, 1]),
                rootedtrees.DominantTree([0]),
                rootedtrees.DominantTree([0, 1, 1])
            ])
        ])
        self.assertEqual(
            struct,
            Funcstruct.from_func(struct.func_form())
        )

    def test_imagepath(self):
        """Check methods for computing structure image paths are equivalent."""
        for i in range(1, 8):
            for struct in EndofunctionStructures(i):
                sim = struct.func_form().imagepath
                fim = struct.imagepath
                np.testing.assert_array_equal(sim, fim)

    def test_struct_counts(self):
        """OEIS A001372: Number of self-mapping patterns."""
        A001372 = [1, 3, 7, 19, 47, 130, 343, 951, 2615, 7318, 20491, 57903]
        for n, count in enumerate(A001372, start=1):
            self.assertEqual(count, len(set(EndofunctionStructures(n))))
            self.assertEqual(count, EndofunctionStructures(n).cardinality())

    def test_degeneracy(self):
        """OEIS A000312: Number of labeled maps from n points to themselves."""
        for i in range(1, 8):
            fac = factorial(i)
            func_count = 0
            for struct in EndofunctionStructures(i):
                func_count += fac//struct.degeneracy
            self.assertEqual(i**i, func_count)

    def test_partition_order_is_unimportant(self):
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
        """Ensure an endofunction structure evaluates to itself"""
        eval_map = {
            'DominantTree': rootedtrees.DominantTree,
            'Necklace': necklaces.Necklace
        }
        struct = Funcstruct(endofunctions.randfunc(30))
        self.assertEqual(struct, eval(repr(struct), globals(), eval_map))