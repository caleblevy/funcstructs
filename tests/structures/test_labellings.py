import unittest
import itertools
import math

from funcstructs.utils.combinat import multinomial_coefficient

from funcstructs.structures.labellings import (
    equipartitions, equipartition_count, ordered_divisions,
    set_partitions, set_partition_count, cycle_labellings,
    cycle_index
)


class LabellingTests(unittest.TestCase):

    split_sets = [(6, 2), (6, 3), (9, 3), (12, 3), (12, 4)]

    def test_equipartition_counts(self):
        """ Check that we produce the correct number of equipartitions. """
        for n, b in self.split_sets:
            self.assertEqual(
                equipartition_count(n, b),
                len(set(equipartitions(range(n), b)))
            )

    def test_equipartition_lengths(self):
        """Make sure each equipartition is a partition of the original set"""
        for n, b in self.split_sets:
            for division in equipartitions(range(n), b):
                s = set(itertools.chain.from_iterable(division))
                self.assertEqual(n, len(s))

    partitions = [[3, 3, 2, 1], [3, 3, 4], [3, 3, 2, 2], [2, 2, 1]]

    def test_ordered_division_counts(self):
        """Check we produce the correct number of ordered partitions."""
        for partition in self.partitions:
            self.assertEqual(
                multinomial_coefficient(partition),
                len(set(ordered_divisions(partition)))
            )

    def test_ordered_division_lengths(self):
        """Check that each ordered partition is a partition S"""
        for partition in self.partitions:
            n = sum(partition)
            for division in ordered_divisions(partition):
                self.assertEqual(
                    n, len(set(itertools.chain.from_iterable(division))))

    def test_set_partition_counts(self):
        """Check we produce the correct number of set partitions"""
        for partition in self.partitions:
            self.assertEqual(
                set_partition_count(partition),
                len(set(set_partitions(partition)))
            )
        self.assertEqual(
            set_partition_count([3, 3, 2], 9),
            len(set(set_partitions([3, 3, 2], 9)))
        )
        self.assertEqual(
            len(set(set_partitions([2, 2], 5))),
            len(set(set_partitions([2, 2, 1])))
        )

    def test_set_partition_lengths(self):
        """Check that each ordered partition is a partition S"""
        for partition in self.partitions:
            n = sum(partition)
            for division in set_partitions(partition):
                self.assertEqual(
                    n, len(set(itertools.chain.from_iterable(division))))

    def test_cycle_labellings(self):
        """Test that we produce the correct number of cycle labellings."""
        for partition in self.partitions:
            self.assertEqual(
                cycle_index(partition),
                len(frozenset(cycle_labellings(partition)))
            )
        self.assertEqual(
            cycle_index([3, 3, 2], 9),
            len(frozenset(cycle_labellings([3, 3, 2], 9)))
        )
        self.assertEqual(
            len(frozenset(cycle_labellings([2, 2], 5))),
            len(frozenset(cycle_labellings([2, 2, 1])))
        )
