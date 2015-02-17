import unittest
from endofunction_structures.productrange import *

class ProductrangeTest(unittest.TestCase):

    def testRangelen(self):
        ranges = [
            [0], [1], [1, 2], [-1, 2], [2, -1], [-1], [0, -1, 1],
            [0, -1, -1], [0, 100, 10], [0, 100, 101], [0, 101, 10],
            [2], [-10, -20, -2], [-10, -21, -2], [2**128+1, 2**128+178, 45]
        ]
        for r in ranges:
            self.assertEqual(len(range(*r)), rangelen(*r))

    def testProductRange(self):
        begins = [[1], None,   0,      1,      [1]*4,   [3]*4,  (1, 2, 3, 3)]
        ends = [[0],   [4]*4,  [4]*4,  [7]*3,  [10]*4,  [6]*4,  (2, 4, 8, 10)]
        steps = [None, 1,      None,   2,      3,       None,   (1, 1, 2, 2)]
        counts = [0,   4**4,   4**4,   3**3,   3**4,    3**4,   1*2*3*4]

        begins.extend([(1, 2, 3), (1, 2, 3)])
        ends.extend([(-9, 9, 9),  (9, -9, 9)])
        steps.extend([(-3, 3, 3), (3, -3, 3)])
        counts.extend([4*3*2,     4*3*2])
        for c, b, e, s in zip(counts, begins, ends, steps):
            self.assertEqual(c, len(list(product_range(b, e, s))))
            self.assertEqual(c, len(list(rev_range(b, e, s))))