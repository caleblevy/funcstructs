import unittest
from endofunction_structures.subsequences import *

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

    def testMonotoneSubsequences(self):
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

        self.assertSequenceEqual(inc, list(increasing_subsequences(seq)))
        self.assertSequenceEqual(nondec, list(nondecreasing_subsequences(seq)))
        self.assertSequenceEqual(dec, list(decreasing_subsequences(seq)))
        self.assertSequenceEqual(noninc, list(nonincreasing_subsequences(seq)))

        inc2 = [1, 2, 3, 4, 5]
        # Test the end isn't double counted.
        self.assertSequenceEqual([inc2], list(increasing_subsequences(inc2)))

    def testSubsequencesStartingwith(self):
        teststart = lambda seq: startswith(seq, lambda x: x == 1)

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
            self.assertSequenceEqual(subseq, list(teststart(seq)))

    def testSubsequencesEndingwith(self):
        testend = lambda seq: endswith(seq, lambda x: x == 1)

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
            self.assertSequenceEqual(subseq, list(testend(seq)))
