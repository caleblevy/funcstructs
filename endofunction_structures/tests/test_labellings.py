import unittest
import itertools

from endofunction_structures import productrange, rootedtrees, counts

from endofunction_structures.labellings import (
    equipartitions, equipartition_count,
    ordered_partitions, ordered_partition_count,
    set_partitions, set_partition_count,
    cycle_labellings, cycle_index,
    tree_labellings
)


class LabellingTests(unittest.TestCase):

    split_sets = [(6, 2), (6, 3), (9, 3), (12, 3), (12, 4)]

    def test_equipartition_counts(self):
        """ Check that we produce the correct number of equipartitions. """
        for n, b in self.split_sets:
            self.assertEqual(equipartition_count(n, b),
                             len(frozenset(equipartitions(range(n), b))))

    def test_even_division_lengths(self):
        """Make sure each equipartition is a partition of the original set"""
        for n, b in self.split_sets:
            for division in equipartitions(range(n), b):
                s = set(itertools.chain.from_iterable(division))
                self.assertEqual(n, len(s))

    partitions = [[3, 3, 2, 1], [3, 3, 4], [3, 3, 2, 2], [2, 2, 1]]

    def test_ordered_partition_counts(self):
        """Check we produce the correct number of ordered partitions."""
        for partition in self.partitions:
            self.assertEqual(
                ordered_partition_count(partition),
                len(set(ordered_partitions(partition)))
            )

    def test_ordered_partition_lengths(self):
        """Check that each ordered partition is a partition S"""
        for partition in self.partitions:
            n = sum(partition)
            for division in ordered_partitions(partition):
                self.assertEqual(n, len(set(productrange.flatten(division))))

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
                self.assertEqual(n, len(set(productrange.flatten(division))))

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

    trees = [
        rootedtrees.DominantTree([1, 2, 3, 3, 2, 3, 3, 2]),
        rootedtrees.DominantTree([1, 2, 3, 3, 2, 3, 3, 4, 5])
    ]

    def test_tree_label_count(self):
        """Ensure each tree has the correct number of representations"""
        for tree in self.trees:
            self.assertEqual(
                counts.factorial(len(tree))//tree.degeneracy(),
                len(set(tree_labellings(tree)))
            )

    def test_trees_are_equivalent(self):
        """Ensure each endofunction is a representation of the original."""
        for tree in self.trees:
            for f in itertools.islice(tree_labellings(tree), 5040):
                self.assertEqual(tree, f.tree_form())
