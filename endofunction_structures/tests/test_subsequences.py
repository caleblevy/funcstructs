# Copyright (C) 2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.

import unittest

from endofunction_structures.subsequences import (
    increasing, decreasing, nonincreasing, nondecreasing, startswith, endswith
)


class SubsequenceTests(unittest.TestCase):
    seqs = [
        [1, 2, 3, 3, 2, 3, 1, 2, 1, 1, 2, 2, 1, 2],
        [2, 2, 3, 3, 4, 2],
        [1],
        [2],
        [4, 3, 2, 1],
        [4, 3, 2, 1, 2, 3, 4],
        [4, 4, 4, 1, 1],
        [1, 1, 1, 1]
    ]

    def test_monotone_subsequences(self):
        """Test that subsequences are monotonic for given comparison
        operations."""
        seq = [1, 2, 3, 4, 3, 3, 2, 3, 4, 5, 4, 5, 3, 3, 2, 3, 4, 5, 6, 5, 5,
               5, 5]

        inc = [[1, 2, 3, 4], [3], [3], [2, 3, 4, 5], [4, 5], [3], [3],
               [2, 3, 4, 5, 6], [5], [5], [5], [5]]
        nondec = [[1, 2, 3, 4], [3, 3], [2, 3, 4, 5], [4, 5], [3, 3],
                  [2, 3, 4, 5, 6], [5, 5, 5, 5]]
        dec = [[1], [2], [3], [4, 3], [3, 2], [3], [4], [5, 4], [5, 3], [3, 2],
               [3], [4], [5], [6, 5], [5], [5], [5]]
        noninc = [[1], [2], [3], [4, 3, 3, 2], [3], [4], [5, 4], [5, 3, 3, 2],
                  [3], [4], [5], [6, 5, 5, 5, 5]]

        self.assertSequenceEqual(inc, list(increasing(seq)))
        self.assertSequenceEqual(nondec, list(nondecreasing(seq)))
        self.assertSequenceEqual(dec, list(decreasing(seq)))
        self.assertSequenceEqual(noninc, list(nonincreasing(seq)))

        inc2 = [1, 2, 3, 4, 5]
        # Test the end isn't double counted.
        self.assertSequenceEqual([inc2], list(increasing(inc2)))

    def test_startswith(self):
        """Make sure leading subsequence terms satisfy the given criterion"""
        startseqs = [
            [[1, 2, 3, 3, 2, 3], [1, 2], [1], [1, 2, 2], [1, 2]],
            [[2, 2, 3, 3, 4, 2]],
            [[1]],
            [[2]],
            [[4, 3, 2], [1]],
            [[4, 3, 2], [1, 2, 3, 4]],
            [[4, 4, 4], [1], [1]],
            [[1], [1], [1], [1]]
        ]

        for seq, subseq in zip(self.seqs, startseqs):
            self.assertSequenceEqual(subseq, list(startswith(seq, 1)))

    def test_endswith(self):
        """Make sure final subsequence terms satisfy the given criterion."""

        endseqs = [
            [[1], [2, 3, 3, 2, 3, 1], [2, 1], [1], [2, 2, 1], [2]],
            [[2, 2, 3, 3, 4, 2]],
            [[1]],
            [[2]],
            [[4, 3, 2, 1]],
            [[4, 3, 2, 1], [2, 3, 4]],
            [[4, 4, 4, 1], [1]],
            [[1], [1], [1], [1]]
        ]

        for seq, subseq in zip(self.seqs, endseqs):
            self.assertSequenceEqual(subseq, list(endswith(seq, 1)))
