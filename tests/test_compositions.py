import unittest
from endofunction_structures.compositions import *

class CompositionTests(unittest.TestCase):

    def test_counts(self):
        n = 10
        for i in range(1, n):
            self.assertEqual(2**(i-1), len(list(compositions_simple(i))))
            self.assertEqual(2**(i-1), len(list(compositions_binary(i))))

    def testCompositionSums(self):
        n = 10
        for i in range(1, n):
            for comp in compositions_simple(i):
                self.assertEqual(i, sum(comp))
            for comp in compositions_binary(i):
                self.assertEqual(i, sum(comp))