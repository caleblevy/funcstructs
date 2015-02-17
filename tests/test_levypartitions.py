import unittest
from endofunction_structures.levypartitions import *

class LevyPartitionTests(unittest.TestCase):

    def testSmallestPartition(self):
        N = 20
        for n in range(1, N):
            for L in range(1, n+1):
                mp = minimal_partition(n, L)
                self.assertTrue(max(mp) - min(mp) in [0, 1])
                self.assertTrue(len(mp) == L)
                self.assertTrue(sum(mp) == n)

    def testFixedLexPartitions(self):
        """Check that the fixed length lex partition outputs are correct."""
        N = 15
        for n in range(N):
            pn = [list(p) for p in lex_partitions(n)]
            np = 0
            for L in range(n+1):
                pnL = [list(p) for p in fixed_lex_partitions(n, L)]
                np += len(pnL)
                # Check for the right order
                self.assertSequenceEqual(pnL, [p for p in pn if len(p) == L])
            # Check for the right number
            self.assertEqual(np, len(pn))

    def testPartitionNumbers(self):
        A000041 = [1, 1, 2, 3, 5, 7, 11, 15, 22, 30, 42, 56, 77, 101, 135]
        for n, count in enumerate(A000041):
            self.assertEqual(count, partition_number(n))
