#!/usr/bin/env python
# Copyright (C) 2014-2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.

"""
A necklace is a class of n-character strings equivalent under rotation (orbits
of the set of n-character strings under the action of cyclic permutation by the
cyclic group). For example, the following are examples of a necklace using
[a,b,c,d], [a,b,b] and [c,d]:

    [a,b,c,d] ~ [b,c,d,a] ~ [c,d,a,b] ~ [d,a,b,c]
    [a,b,b] ~ [b,a,b] ~ [b,b,a]
    [c,d,c,d] ~ [d,c,d,c]

Different necklaces may have different periodicity, as seen above. This module
contains a collection of functions for counting and enumerating necklaces of a
given multiset.

Their relavence to enumerating endofunction structures is as follows: given a
collection of N forests, the necklaces whose beads are the forests' trees are
precisely the distinct ways of connecting the trees to form a cycle of length
n. Thus the ways of connecting a collection of rooted trees together in a cycle
are precisely the necklaces whose beads are the rooted trees.
"""


import fractions
import functools
import collections
import unittest

import factorization
import multiset


def periodicity(strand):
    """ Find the "periodicity" of a list; i.e. the number of its distinct
    cyclic rotations. Algorithm proposed by Meng Wang (wangmeng@berkeley.edu)
    runs in O(len(strand)). """
    n = len(strand)
    if n in [0, 1]:
        return n
    seed = []
    l = p = 1
    while p != n:
        while not factorization.isdivisor(l, n):
            l += 1
        p = l
        seed.extend(strand[len(seed):p])
        stop = False
        for rep in range(l, n, l):
            for i, val in enumerate(seed):
                l += 1
                if val != strand[rep + i]:
                    stop = True
                    break
            if stop:
                break
        # for-else loop break
        else:
            break
    return len(seed)


class Necklace(object):
    """An equivalence class of all lists equivalent under rotation."""

    def __init__(self, strand):
        """Initialize the necklace. Items in the necklace must be hashable
        (immutable), otherwise the equivalence class could change
        dynamically."""
        period = periodicity(strand)
        self.period = period
        self.reps = len(strand)//period
        self.seed = collections.deque(strand[:period])
        self.beads = multiset.Multiset(strand)
        self.strand = list(strand)

    def __repr__(self):
        return "Necklace(%s)"%str(self.strand)

    def __len__(self):
        return self.period * self.reps

    def __hash__(self):
        """If n1==n2, hash is equal, but quite degenerate."""
        return hash(tuple([self.beads, self.period]))

    def __eq__(self, other):
        """For now we check for equality by "brute force" rotation, as D.
        Eppstein's normalization algorithm produces unpredictable output for
        items with ill-defined orderability."""
        if isinstance(other, self.__class__):
            if self.reps == other.reps:
                if self.period == other.period:
                    if self.beads == other.beads:
                        for I in range(self.period):
                            if self.seed == other.seed:
                                return True
                            other.seed.rotate()
        return False

    def __ne__(self, other):
        return not self == other

    __lt__ = None

    def __contains__(self, other):
        try:
            return self == self.__class__(other)
        except:
            return False


# We may canonically represent a multiset with an unordered partition
# corresponding to the multiplicities of the elements. It is simpler to
# enumerate necklaces on a canonical partition and then match those to
# necklaces formed from the beads.

def partition_necklace_count_by_period(partition):
    """ Given a partition of multiplicities, returns the number of necklaces on
    this partition of beads of each possible period of the necklace. To do
    this, we start with the smallest divisor of the gcd of all the
    multiplicities, and find all necklaces with period less than or equal to
    this divisor.

    Before normalizing by the period of the necklace (to account for its
    distinct rotations) we subtract the number of necklaces with each period
    which is a subdivisor of our given period, to ensure we give the number of
    necklaces with exactly period k. """

    k = len(partition)
    N = sum(partition)
    w = functools.reduce(fractions.gcd, partition)
    p0 = N//w

    factors = factorization.divisors(w)
    beads = [0]*factors[-1]

    # Find the multiplicity of each period
    for factor in factors:
        n = period = factor*p0
        beads[factor-1] = 1
        # The number of character permutations which are periodic in at most
        # "factor" is simply the multinomial coefficient corresponding to that
        # subset of the multiplicity partition.
        for I in range(k):
            beads[factor-1] *= multiset.nCk(n, partition[I]*factor//w)
            n -= partition[I]*factor//w

        # Subtact off the number of necklaces whose period subdivides our
        # divisor of w, to make sure beads[factor-1] give the EXACTLY the
        # number of necklaces with period k.
        subdivisors = factorization.divisors(factor)
        if subdivisors[-1] != 1:
            for subfactor in subdivisors[:-1]:
                beads[factor-1] -= subfactor*p0*beads[subfactor-1]

        # Finally, normalize by the period, the number of distinct rotations of
        # any member of beads[k].
        beads[factor-1] //= period
    return beads


def necklace_count_by_period(beads):
    """ Returns a list whose kth element is the number of necklaces
    corresponding to the input set of beads with k+1 distinct rotations. """
    _, partition = multiset.Multiset(beads).split()
    return partition_necklace_count_by_period(partition)


def partition_necklace_count(partition):
    return sum(partition_necklace_count_by_period(partition))

necklace_count = lambda items: sum(necklace_count_by_period(items))


def partition_necklaces(partition):
    """Wrapper for partition necklaces, which takes a partition of
    multiplicities and enumerates canonical necklaces on that partition."""

    partition = list(partition)
    a = [0]*sum(partition)
    partition[0] -= 1
    k = len(partition)
    return _partition_necklaces(a, partition, 2, 1, k)


def _partition_necklaces(a, partition, t, p, k):
    """ This function is a result of refactoring of Sage's
    _simple_fixed_content algorithm, featured in Sage at
    https://github.com/sagemath/sage.git, located in
    src/sage/combinat/neckalce.py as of December 23, 2014.


    The original code was written by Mike Hansen <mhansen@gmail.com> in 2007,
    who based his algorithm on

        Sawada, Joe. "A fast algorithm to generate necklaces with fixed
        content", Theoretical Computer Science archive Volume 301 , Issue 1-3,
        May 2003.
    """
    n = len(a)
    if t > n and not(n % p):
        yield a
    else:
        for j in range(a[t-p-1], k):
            if partition[j] > 0:
                a[t-1] = j
                partition[j] -= 1
                tp = p if(j == a[t-p-1]) else t
                for z in _partition_necklaces(a, partition, t+1, tp, k):
                    yield z
                partition[j] += 1


def necklaces(items):
    """ Given a set of items (called beads) returns all necklaces which can be
    made with those beads. """

    if not items:
        return
    items = sorted(items)
    y, d = multiset.Multiset(items).split()
    for necklace in partition_necklaces(d):
        # Explicitly make a tuple, since we must form the list of all necklaces
        # in memory when constructing endofunction structures.
        yield tuple([y[I] for I in necklace])


class NecklaceTests(unittest.TestCase):

    def testNecklaceCounts(self):
        color_partitions = [[3, 3, 2], [4, 4, 4, 3, 3, 2, 1, 1], [24, 36]]
        color_cardinalities = [70, 51330759480000, 600873126148801]
        for cp, cc in zip(color_partitions, color_cardinalities):
            self.assertEqual(cc, sum(partition_necklace_count_by_period(cp)))

    def test_necklace_init(self):
        n = Necklace([1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3])
        self.assertEqual(n.period, 3)
        self.assertEqual(n.reps, 4)
        self.assertEqual(n.seed, collections.deque([1, 2, 3]))
        self.assertEqual(n.beads, multiset.Multiset([1, 2, 3]*4))

    def test_necklace_equality(self):
        n = Necklace([1, 2, 3, 1, 2, 3])
        nshort = Necklace([1, 2, 3])
        nlong = Necklace([1, 2, 3, 1, 2, 3, 1, 2, 3])
        nrot = Necklace([3, 1, 2, 3, 1, 2])
        ntype = Necklace(tuple([2, 3, 1, 2, 3, 1]))

        self.assertNotEqual(n, nshort)
        self.assertNotEqual(n, nlong)
        self.assertEqual(n, nrot)
        self.assertEqual(n, ntype)

    def test_necklace_containement(self):
        n = Necklace([1, 2, 3, 1, 2, 3])
        self.assertFalse(n in n)
        self.assertTrue(tuple([3, 1, 2, 3, 1, 2]) in n)

    def test_necklace_hash(self):
        self.assertEqual(hash(Necklace([1, 2, 3])), hash(Necklace([3, 1, 2])))

    def test_necklace_repr(self):
        n = Necklace([1, 2, 3, 1, 2, 3])
        self.assertTrue(n == eval(repr(n)))

    def testNecklaces(self):
        beadsets = [
            [4, 4, 5, 5, 2, 2, 2, 2, 2, 2, 6, 6],
            [4, 4, 5, 5, 2, 2, 2, 2, 2, 2, 6, 6, 6],
            [0]
        ]
        for beadset in beadsets:
            count = 0
            for necklace in necklaces(beadset):
                count += 1
            self.assertEqual(necklace_count(beadset), count)

    def test_periodicities(self):
        periods = []
        lists = []

        N = 20
        for n in range(1, N+1):
            for d in factorization.divisors(n):
                periods.append(d)
                lists.append(([0]+[1]*(d-1))*(n//d))

        t1 = [(1, 2), ]*3+[(1, 1)]
        t2 = t1*3 + [(1, 4, 3)]*3 + [(1, )]
        t3 = t2*2 + [(2, )]*3 + [(1, 4, 3)]
        t4 = t3*3 + [(3, )]*3+[(1, 2)]
        lists.append(t4*4)
        periods.append(112)

        lists.extend([[(1, 2), (1, 2)], [(1, 2), (1, )]])
        periods.extend([1, 2])

        lists.append([(1, 2), (1, ), (1, 2), (1, ), (1, )])
        periods.append(5)

        lists.append([(1, 2), (1, ), (1, 2), (1, ), (1, 2)])
        periods.append(5)

        for period, lst in zip(periods, lists):
            self.assertEqual(period, periodicity(lst))


if __name__ == '__main__':
    unittest.main()
