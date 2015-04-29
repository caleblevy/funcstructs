import unittest

from ..productrange import productrange, rev_range


class ProductrangeTest(unittest.TestCase):

    def test_productrange(self):
        """Test number of outputs in the product range is correct."""
        # Columns are numel, begin, end, step
        ranges = [
            (0, [1], [0], None),
            (4**4, None, [4]*4, None),
            (4**4, 0, [4]*4, None),
            (3**3, 1, [7]*3, 2),
            (3**4, [1]*4, [10]*4, 3),
            (3**4, [3]*4, [6]*4, None),
            (1*2*3*4, (1, 2, 3, 3), (2, 4, 8, 10), (1, 1, 2, 2)),
            (4*3*2, (1, 2, 3), (-9, 9, 9), (-3, 3, 3)),
            (4*3*2, (1, 2, 3), (9, -9, 9), (3, -3, 3))
        ]
        for num, begin, end, step in ranges:
            self.assertEqual(num, len(list(productrange(begin, end, step))))
            self.assertEqual(num, len(list(rev_range(begin, end, step))))
