import unittest

from PADS import IntegerPartitions

from ..levypartitions import (
    isqrt,
    minimal_partition,
    fixed_lex_partitions,
    partition_number
)


class LevyPartitionTests(unittest.TestCase):

    def test_integer_root(self):
        """Test r = isqrt(n) is greatest integer such that r**2 <= n."""
        for val in list(range(1000)) + [2**87+2**41+1] + [2**96]:
            self.assertTrue(isqrt(val)**2 <= val)
            self.assertTrue(val < (isqrt(val)+1)**2)

    def test_minimal_partition(self):
        """Ensure partitions are lexicographically smallest"""
        N = 20
        for n in range(1, N):
            for L in range(1, n+1):
                mp = minimal_partition(n, L)
                self.assertTrue(max(mp) - min(mp) in [0, 1])
                self.assertTrue(len(mp) == L)
                self.assertTrue(sum(mp) == n)

    def test_fixed_lex_partitions(self):
        """Check that the fixed length lex partition outputs are correct."""
        N = 15
        for n in range(N):
            pn = [list(p) for p in IntegerPartitions.lex_partitions(n)]
            np = 0
            for L in range(n+1):
                pnL = [list(p) for p in fixed_lex_partitions(n, L)]
                np += len(pnL)
                # Check for the right order
                self.assertSequenceEqual([p for p in pn if len(p) == L], pnL)
            # Check for the right number
            self.assertEqual(np, len(pn))

    def test_partition_counts(self):
        """Check our pentagonal number theorem based partition counter."""
        A000041 = [1, 1, 2, 3, 5, 7, 11, 15, 22, 30, 42, 56, 77, 101, 135]
        for n, count in enumerate(A000041):
            self.assertEqual(count, partition_number(n))
