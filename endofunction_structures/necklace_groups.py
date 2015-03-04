#!/usr/bin/env python
# Copyright (C) 2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.

import unittest

from . import counts
from . import polynomials
from . import levypartitions
from . import necklaces


def count_by_period(beads):
    return necklaces.FixedContentNecklaces(beads).count_by_period()


def period_combos(beads, reps):
    """All possible combinations of periods from given counts by period"""
    necklace_counts = count_by_period(beads)
    periods = [i for i, val in enumerate(necklace_counts) if val]
    for part in levypartitions.max_length_partitions(reps, len(periods)):
        for combo in polynomials.multisets_with_multiplicities(periods, part):
            yield combo


def period_combo_count(necklace_counts, combo):
    """Number of necklaces from a combination of periods"""
    val = 1
    for period, mult in combo.items():
        val *= counts.nCWRk(necklace_counts[period], mult)
    return val


def necklace_groups_by_period_combo(beads, reps):
    """Return generator yield pairs of period groups and their counts"""
    necklace_counts = count_by_period(beads)
    for combo in period_combos(beads, reps):
        yield combo, period_combo_count(necklace_counts, combo)


class NecklaceGroupTests(unittest.TestCase):

    def test_necklace_group_by_period_combo_counts(self):
        necks = [[1]*4+[2]*4+[3]*4, [0]*24+[1]*36]
        for n in necks:
            self.assertEqual(
                counts.nCWRk(sum(count_by_period(n)), 4),
                sum(i for _, i in necklace_groups_by_period_combo(n, 4))
            )


if __name__ == '__main__':
    unittest.main()
