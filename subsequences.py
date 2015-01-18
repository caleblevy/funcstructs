#!/usr/bin/env python
# Copyright (C) 2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.

from operator import gt, ge, le, lt
import unittest


def monotone_subsequences(seq, comparison):
    """
    Given an iterable seq and a comparsion function, returns a generator of the
    subsequences of seq such that comparison(seq[I],seq[I+1]) holds for
    0<=I<=len(seq)-1.

    For example, if comparison is >=, then this returns nondecreasing
    subsequences, while comparison of > returns increasing. Equivalent to
    sympy's runs() method.
    """
    if not seq:
        return
    subseq = [seq[0]]
    term_prev = seq[0]
    for term in seq[1:]:
        if comparison(term, term_prev):
            subseq.append(term)
        else:
            yield subseq
            subseq = [term]
        term_prev = term
    yield subseq

increasing_subsequences = lambda seq: monotone_subsequences(seq, gt)
nondecreasing_subsequences = lambda seq: monotone_subsequences(seq, ge)
decreasing_subsequences = lambda seq: monotone_subsequences(seq, lt)
nonincreasing_subsequences = lambda seq: monotone_subsequences(seq, le)


def breakat(seq, cond):
    """
    Given a sequence seq and boolean function of a single input cond, returns a
    generator of subsequences such that a new subsequence begins if and only if
    cond is true for the first element in the subsequence. If cond is never
    true, returns the original sequence.
    """
    if not seq:
        return
    subseq = [seq[0]]
    if len(seq) == 1:
        yield subseq
        return
    for ind, el in enumerate(seq[1:]):
        if cond(el):
            yield subseq
            subseq = [el]
        else:
            subseq.append(el)
    yield subseq


class SubsequenceTest(unittest.TestCase):

    def testMonotoneSubsequences(self):
        test_tree = [1, 2, 3, 4, 3, 3, 2, 3, 4, 5, 4, 5, 3, 3, 2, 3, 4, 5, 6,
                     5, 5, 5, 5]

        inc = [
            [1, 2, 3, 4], [3], [3], [2, 3, 4, 5], [4, 5], [3], [3],
            [2, 3, 4, 5, 6], [5], [5], [5], [5]
        ]
        nondec = [
            [1, 2, 3, 4], [3, 3], [2, 3, 4, 5], [4, 5], [3, 3],
            [2, 3, 4, 5, 6], [5, 5, 5, 5]
        ]
        dec = [
            [1], [2], [3], [4, 3], [3, 2], [3], [4], [5, 4], [5, 3], [3, 2],
            [3], [4], [5], [6, 5], [5], [5], [5]
        ]
        noninc = [
            [1], [2], [3], [4, 3, 3, 2], [3], [4], [5, 4], [5, 3, 3, 2], [3],
            [4], [5], [6, 5, 5, 5, 5]
        ]

        self.assertEqual(inc, list(increasing_subsequences(test_tree)))
        self.assertEqual(nondec, list(nondecreasing_subsequences(test_tree)))
        self.assertEqual(dec, list(decreasing_subsequences(test_tree)))
        self.assertEqual(noninc, list(nonincreasing_subsequences(test_tree)))

        inc2 = [1, 2, 3, 4, 5]
        # Test the end isn't double counted.
        self.assertEqual([inc2], list(increasing_subsequences(inc2)))

    def testBreakpointSequences(self):
        testat = lambda seq: breakat(seq, lambda x: x == 1)
        seqs = [
            [1, 2, 3, 3, 2, 3, 1, 2, 1, 1, 2, 2, 1, 2],
            [2, 2, 3, 3, 4, 2],
            [1],
            [4, 3, 2, 1],
            [4, 3, 2, 1, 2, 3, 4],
            [4, 4, 4, 1, 1],
            [1, 1, 1, 1]
        ]

        subseqs = [
            [[1, 2, 3, 3, 2, 3], [1, 2], [1], [1, 2, 2], [1, 2]],
            [[2, 2, 3, 3, 4, 2]],
            [[1]],
            [[4, 3, 2], [1]],
            [[4, 3, 2], [1, 2, 3, 4]],
            [[4, 4, 4], [1], [1]],
            [[1], [1], [1], [1]]
        ]

        for seq, subseq in zip(seqs, subseqs):
            self.assertEqual(subseq, list(testat(seq)))


if __name__ == '__main__':
    unittest.main()