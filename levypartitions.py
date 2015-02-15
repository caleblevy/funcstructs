#!/usr/bin/env python
# Copyright (C) 2014-2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.


""" Further modules for enumerating and counting partitions, mostly derived by
myself. """



import unittest
import itertools

from PADS.IntegerPartitions import partitions, lex_partitions


def isqrt(n):
    """ Faster method of iroot for the particular case of the integer square
    root. Code taken directly from "Integer square root in python" at
    http://stackoverflow.com/a/15391420. """
    x = n
    y = (x + 1) // 2
    while y < x:
        x = y
        y = (x + n // x) // 2
    return x


def tuple_partitions(n):
    """ Every partition on N may be represented in the form as a tuple of
    numbers (n1,n2,...,nk) with 1<=i<=k such that 1*n1+2*n2+...+k*nk=N. This
    program outputs every partition of n in a tuple format. """

    for part in partitions(n):
        b = [0]*n
        for p in part:
            b[p-1] += 1
        yield b


def _min_part(n, L):
    """ Helper function for fixed_lex_partitions. Returns a tuple containing:
        1) The output of minimal_partition(n,L)
        2) #(Occurances of 1 in this partition)+1.

    The second output is returned so as to avoid calling the count() method of
    the list corresponding to the partition, since this information is
    necessarily contained in the process of its creation. It is needed by
    fixed_lexed_partitions for the index on which to decrement. """
    binsize = n//L
    overstuffed = n - L*binsize
    regular = L - overstuffed
    ones_count = 1 if binsize != 1 else regular + 1
    return [binsize+1]*overstuffed + [binsize]*regular, ones_count


def minimal_partition(n, L):
    """A wrapper for _min_partition. Given integers n > 0 and L <= n, returns
    the lexicographically smallest unordered integer partition of n into L
    nonzero parts."""
    min_part, _ = _min_part(n, L)
    return min_part


def fixed_lex_partitions(n, L):
    """Integer partitions of n into L parts, in lexicographic order. This
    algorithm was derived and implemented by Caleb C. Levy in 2014. Its form
    was taken from David Eppstein's equivalent generator for fixed length
    partitions in colex order."""
    if L == 0:
        if n == 0:
            yield []
        return
    if L == 1:
        if n > 0:
            yield [n]
        return
    if n < L:
        return

    partition, j = _min_part(n, L)
    while True:
        # Algorithm starts with minimal partition, and index of the last 1
        # counting backwards. We then decrement the rightmost components and
        # increment those to their immediate left, up to the point where the
        # partition would beak ordering.
        #
        # Once we have decremented as far as possible, we append the new
        # minimum partition, and repeat.
        yield partition
        k = 2
        s = (j-1) + partition[L-j] - 1
        while j+k-1 < L and partition[L-j-k] == partition[L-j-1]:
            s += partition[L-j-1]
            k += 1
        if j+k-1 > L:
            return
        k -= 1
        partition[L-j-k] += 1
        partition[L-j-k+1:], j = _min_part(s, j+k-1)


def partition_numbers_upto(N):
    """ Uses Euler's Pentagonal Number Theorem to count partition number using
    the previous terms. The sum is taken over O(sqrt(n)) terms on each pass, so
    the algorithm runs in O(n**3/2). See the Knoch paper in papers folder for a
    proof of the theorem. """
    if N == 0:
        return [1]
    P = [1]+[0]*N
    for n in range(1, N+1):
        k_max = (isqrt(24*n+1)-1)//6
        k_min = -((isqrt(24*n+1)+1)//6)
        for k in itertools.chain(range(k_min, 0), range(1, k_max+1)):
            P[n] += (-1)**abs((k-1)) * P[n-k*(3*k+1)//2]
    return P

partition_number = lambda n: partition_numbers_upto(n)[-1]


class LevyPartitionTest(unittest.TestCase):

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


if __name__ == '__main__':
    unittest.main()
