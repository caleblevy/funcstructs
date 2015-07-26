import unittest
from math import factorial

from funcstructs.structures import (
    randfunc,
    Endofunction,
    DominantSequence,
    Necklace
)

from funcstructs.structures.conjstructs import (
    Funcstruct,
    EndofunctionStructures
)


class FuncstructTests(unittest.TestCase):

    s = super(Funcstruct, Funcstruct).__new__(Funcstruct, [
            Necklace([
                DominantSequence([0, 1, 2]),
                DominantSequence([0, 1, 1])
            ]),
            Necklace([
                DominantSequence([0, 1])
            ]),
            Necklace([
                DominantSequence([0, 1, 1]),
                DominantSequence([0]),
                DominantSequence([0, 1, 1])
            ])
        ])

    def test_func_form(self):
        """Convert struct to func and back, and check we get the same thing."""
        self.assertEqual(self.s, Funcstruct(self.s.func_form()))

    def test_imagepath(self):
        """Check methods for computing structure image paths are equivalent."""
        for i in range(1, 8):
            for struct in EndofunctionStructures(i):
                sim = struct.func_form().imagepath()
                fim = struct.imagepath()
                self.assertSequenceEqual(sim, fim)

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
                func_count += fac//struct.degeneracy()
            self.assertEqual(i**i, func_count)

    def test_len(self):
        """Test Funcstruct properly overrides Multiset.__len__"""
        self.assertEqual(15, len(self.s))
        self.assertEqual(30, len(Funcstruct(randfunc(30))))

    def test_repr(self):
        """Ensure an endofunction structure evaluates to itself"""
        struct = Funcstruct(randfunc(30))
        self.assertEqual(struct, eval(repr(struct)))
