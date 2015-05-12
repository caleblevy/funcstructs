import unittest

import numpy as np

from funcstructs.structures import *
from ..floatfuncs import *


class FloatSetTests(unittest.TestCase):

    finite = [Min16, Zero, One, Max16]
    nonfinite = [-Inf, NaN, Inf]
    fin = FloatSet(finite)
    nfi = FloatSet(nonfinite)

    def test_init_errors(self):
        # Make sure error is raised for non-float16
        with self.assertRaises(TypeError):
            FloatSet([np.float32('inf')])
        with self.assertRaises(TypeError):
            FloatSet([np.float64('nan'), 1, 2])
        # Make sure duplicates are not allowed
        with self.assertRaises(ValueError):
            FloatSet(self.finite + self.finite)

    def test_addition(self):
        # Cannot add elements with duplicates
        with self.assertRaises(ValueError):
            self.fin + self.fin
        e = self.fin + self.nfi
        self.assertEqual(7, len(e))
        for f in self.finite + self.nonfinite:
            self.assertIn(f, e)

    def test_float_lists(self):
        for fset in [
            Negatives, NonNegatives, Positives, NonPositives,
            FiniteNonNegatives, FiniteNonPositives, FiniteNegatives,
            FinitePositives, UnitInterval, Finites, NonNan, Floats
        ]:
            self.assertIsInstance(fset, FloatSet)

    def test_conjugation(self):
        f = {x: x for x in self.finite}
        g = {x: x for x in self.finite[:-1]}
        h = {x: x for x in self.nonfinite}
        # Order should be independent of dict
        self.assertEqual(
            Endofunction(range(4)),
            self.fin.conj(f)
        )
        self.assertEqual(
            Endofunction(range(3)),
            self.nfi.conj(h)
        )
        # Subdomain
        with self.assertRaises(ValueError):
            self.fin.conj(g)
        # Wrong domain
        with self.assertRaises(KeyError):
            self.fin.conj(h)
