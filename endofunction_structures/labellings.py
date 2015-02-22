#!/usr/bin/env python
# Copyright (C) 2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.

import math
import itertools
import unittest

import multiset

class SetPartition(object):
    def __init__(self, S):
        pass
        # if len(set(S)) != len(S):
        #  print warning
        # if isinstance(S, int):
        #  S = set(range(S))


def multinomial_coefficient(partition, n=None):
    """Number of ordered combinations into the given partition. """
    if n is None:
        n = sum(partition)
    coeff = 1
    for p in partition:
        coeff *= multiset.nCk(n, p)
        n -= p
    return coeff


def _ordered_divisions(S, partition):
    if len(partition) == 1:
        yield [frozenset(S)]
    else:
        for first_combo in itertools.combinations(S, partition[0]):
            for remaining_combos in _ordered_divisions(S - set(first_combo), partition[1:]):
                yield [frozenset(first_combo)] + remaining_combos


def ordered_divisions(S, partition):
    S = set(S)
    if not len(S) == sum(partition):
        raise ValueError("partition must sum to size of set")
    for p in _ordered_divisions(S, partition):
        yield tuple(p)


def arrangement_count(n, b):

    """The total number of ways of evenly dividing a set S with n elements
    into b parts is n!/((n/b)!^b b!) which we can see as follows:

    Take all the permutations of S of which there are n!. We divide them
    into subsequences of length b. If we then disregard ordering each
    selection of subsequences will appear b! times. Each subsequence in
    each permutation of subsequences has (n/b)! representations, and there
    are b independent bins in each selection.

    Each combination of combinations will thus have (n/b)!**b * b! distinct
    representations. """

    return math.factorial(n)//(math.factorial(n//b)**b)//math.factorial(b)


def _even_divisions(S, b):
    n = len(S)
    if b == 1 or n == 1:
        yield [frozenset(S)]
    else:
        marked_el = (S.pop(), )
        for first_combo in itertools.combinations(S, n//b-1):
            for remaining_combos in _even_divisions(S - set(first_combo), b-1):
                yield [frozenset(marked_el + first_combo)] + remaining_combos


def even_divisions(S, b):
    """Evenly split a set of itmes into b parts."""
    S = set(S)
    if len(S) % b:
        raise ValueError("items must divide evenly")
    for division in _even_divisions(S, b):
        yield frozenset(division)


def partition_division_count(partition, n=None):
    """The total number of ways of partitioning S with n elements into a given
    combination of bin sizes [l1, l2, ..., lk] with multiplicities [m1, m2,
    ..., mk] is given by n!/(l1!^m1 * m1!)/(l2!^m2 * m2!)/.../(lk!^mk * mk!),
    which may be seen as follows:

    List all permutations of S of which there are n!. Order the partition
    arbitrarily, and set division markers in each permutation at those
    locations. The number of appearances of each group of cycles of the same
    length is covered above. We just multiply these together to get the number
    of combinations.

    Alternatively it is the cycle index divided by the factorial of each cycle
    length, including multiplicity, since here permutation order does not
    matter.
    """
    partition = multiset.Multiset(partition)
    if n is None:
        n = sum(partition)
    count = math.factorial(n)
    for l, m in zip(*partition.split()):
        count //= math.factorial(l)**m * math.factorial(m)
    return count

# Just as a side note to myself, there was a moment (today Feb 21 at 6:30 P.M California) when I was looking at the above block of code - (partition_division_count) after having just been examining and comparing it to set_partition.py in sage's project code, and I thought that this function was part of sage's repository; i.e. I thought it could ahve been part of the sage package.


def _unordered_partition_divisions(S, partition):
    lengths, mults = multiset.Multiset(partition).sort_split()
    # clm[i] is the number of nodes situated in some bin of size l[i].
    clm = [l*m for l, m in zip(lengths, mults)]
    for odiv in _ordered_divisions(S, clm):
        strand = []
        for m, cbin in zip(mults, odiv):
            strand.append(_even_divisions(set(cbin), m))
        for bundle in itertools.product(*strand):
            yield frozenset(itertools.chain.from_iterable(bundle))


def unordered_partition_divisions(partition, S=None):
    if S is None:
        S = range(sum(partition))
    elif isinstance(S, int):
        S = range(S)
    else:
        S = set(S)

    for subset in itertools.combinations(S, sum(partition)):
        for p in _unordered_partition_divisions(set(subset), partition):
            yield p


class LabellingTests(unittest.TestCase):

    split_sets = [(6, 2), (6, 3), (9, 3), (12, 3), (12, 4)]

    def test_even_division_counts(self):
        """ Check that we produce the correct number of combinations. """
        for n, b in self.split_sets:
            self.assertEqual(arrangement_count(n, b),
                             len(frozenset(even_divisions(range(n), b))))

    def test_even_division_uniqueness(self):
        """Make sure each division is a partition of the original set"""
        for n, b in self.split_sets:
            for division in even_divisions(range(n), b):
                s = set(itertools.chain.from_iterable(division))
                self.assertEqual(n, len(s))
    
    partitions = [[3, 3, 2, 1], [3, 3, 4], [3, 3, 2, 2], [2, 2, 1]]

    def test_ordered_division_counts(self):
        for partition in self.partitions:
            self.assertEqual(multinomial_coefficient(partition),
                             len(set(ordered_divisions(range(sum(partition)), partition))))

    def test_ordered_partition_sums(self):
        for partition in self.partitions:
            n = sum(partition)
            for division in ordered_divisions(range(sum(partition)), partition):
                s = set(itertools.chain.from_iterable(division))
                self.assertEqual(n, len(s))

    def test_unordered_partition_divisions(self):
        for partition in self.partitions:
            self.assertEqual(partition_division_count(partition),
                             len(frozenset(unordered_partition_divisions(partition))))
        self.assertEqual(partition_division_count([3, 3, 2], 9),
                         len(frozenset(unordered_partition_divisions([3, 3, 2], 9))))
        self.assertEqual(len(frozenset(unordered_partition_divisions([2, 2], 5))),
                         len(frozenset(unordered_partition_divisions([2, 2, 1]))))

if __name__ == '__main__':
    unittest.main()
