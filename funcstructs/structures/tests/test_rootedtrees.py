import unittest
import math

from .. import endofunctions

from ..rootedtrees import (
    RootedTree,
    OrderedTree,
    DominantTree,
    TreeEnumerator,
    ForestEnumerator,
    PartitionForests
)


class TreeEnumerationTests(unittest.TestCase):

    # Counting tests
    A000081 = [1, 1, 2, 4, 9, 20, 48, 115, 286]

    def test_tree_counts(self):
        """OEIS A000081: number of unlabelled rooted trees on N nodes."""
        for n, count in enumerate(self.A000081):
            trees = set()
            for tree in TreeEnumerator(n+1):
                trees.add(tree)
                trees.add(tree)
            self.assertEqual(count, len(trees))
            self.assertEqual(count, TreeEnumerator(n+1).cardinality)

    def test_forest_counts(self):
        """Check len(ForestEnumerator(N))==A000081(N+1)"""
        for n, count in enumerate(self.A000081[1:]):
            forests = set()
            for forest in ForestEnumerator(n+1):
                forests.add(forest)
                forests.add(forest)
            self.assertEqual(count, len(forests))
            self.assertEqual(count, ForestEnumerator(n+1).cardinality)

    def test_partition_forest_counts(self):
        """Check alternate way of enumerating forests."""
        from PADS.IntegerPartitions import partitions
        for n, count in enumerate(self.A000081[1:]):
            forests = set()
            forest_count = 0
            for partition in partitions(n+1):
                forests.update(PartitionForests(partition))
                forest_count += PartitionForests(partition).cardinality
            self.assertEqual(count, len(forests))
            self.assertEqual(count, forest_count)

    def test_tree_degeneracies(self):
        """OEIS A000169: n**(n-1) == number of rooted trees on n nodes."""
        for n in range(1, len(self.A000081)):
            ordered_count = 0
            rooted_count = 0
            nfac = math.factorial(n)
            for tree in TreeEnumerator(n):
                ordered_count += nfac//tree.degeneracy()
                rooted_count += nfac//RootedTree.from_levels(tree).degeneracy()
            self.assertEqual(n**(n-1), ordered_count)
            self.assertEqual(n**(n-1), rooted_count)


class TreeTests(unittest.TestCase):

    def test_rooted_tree_strings(self):
        """Ensure Unordered trees are properly formatted."""
        T = RootedTree.from_levels(
            [1, 2, 3, 4, 5, 5, 4, 5, 5, 2, 3, 4, 5, 5, 4, 5, 5])
        T2 = RootedTree.from_levels(range(1, 5))
        self.assertEqual(str(T), "RootedTree({{{{{}^2}^2}}^2})")
        self.assertEqual(str(T2), "RootedTree({{{{}}}})")

    def test_reprs(self):
        """Test repr(Tree) == Tree for various trees."""
        TreeSeqs = [[1, 2, 3, 4, 5, 5, 4, 5, 5, 2, 3, 4, 5, 5, 4, 5, 5],
                    [1, 2, 3, 4, 5, 4, 5, 5, 2, 3, 2, 3, 4, 4, 5, 6],
                    range(1, 5)]
        for seq in TreeSeqs:
            T_unordered = RootedTree.from_levels(seq)
            T_ordered = OrderedTree(seq)
            T_dominant = DominantTree(seq)
            self.assertEqual(T_unordered, eval(repr(T_unordered)))
            self.assertEqual(T_ordered, eval(repr(T_ordered)))
            self.assertEqual(T_dominant, eval(repr(T_dominant)))
        node_count = [4, 5, 6, 10]
        for n in node_count:
            trees = TreeEnumerator(n)
            forests = ForestEnumerator(n)
            self.assertEqual(trees, eval(repr(trees)))
            self.assertEqual(forests, eval(repr(forests)))
        partitions = [[4, 4, 3], [4, 3, 4], [2, 2, 2, 6]]
        for partition in partitions:
            pforests = PartitionForests(partition)
            self.assertEqual(pforests, eval(repr(pforests)))

    def test_traverse_map(self):
        """Test the bracket representation of these rooted trees."""
        trees = [
            OrderedTree([0, 1, 2, 3, 4, 5, 3, 1, 2, 3]),
            OrderedTree([0, 1, 2, 3, 4, 5, 3, 1, 2, 2]),
            OrderedTree([0, 1, 2, 3, 4, 4, 4, 4, 4, 1]),
        ]
        nestedforms = (
            [[[[[[]]], []]], [[[]]]],
            [[[[[[]]], []]], [[], []]],
            [[[[[], [], [], [], []]]], []]
        )
        for tree, nest in zip(trees, nestedforms):
            self.assertSequenceEqual(nest, tree.traverse_map())

    def test_treefuncs(self):
        """Tests attached tree nodes and canonical_treeorder in one go."""
        for n in range(1, 10):
            for tree in TreeEnumerator(n):
                treefunc = endofunctions.Endofunction.from_levels(tree)
                rtreefunc = endofunctions.randconj(treefunc)
                self.assertEqual(tree, DominantTree.from_func(rtreefunc))

    def test_rootedtree_conversion(self):
        """Test conversion between rooted and unordered trees is seamless."""
        T = DominantTree([0, 1, 2, 3, 4, 4, 3, 4, 4, 1, 2, 3, 4, 3, 3, 4, 4])
        RT = RootedTree.from_levels(T)
        TRT = RT.ordered_form()
        self.assertEqual(T, TRT)

    def test_height_groups(self):
        """Test nodes are grouped correctly by their height"""
        T = OrderedTree([0, 1, 2, 2, 3, 3, 3, 4, 5, 5, 4, 3, 3, 2, 1, 2])
        hg = [[0], [1, 14], [2, 3, 13, 15], [4, 5, 6, 11, 12], [7, 10], [8, 9]]
        for height, group in enumerate(T.height_groups()):
            self.assertSequenceEqual(hg[height], group)
            self.assertEqual(height, list(set(map(T.__getitem__, group)))[0])

    def test_height_independence(self):
        """Check that tree methods are unaffected by root height"""
        T = OrderedTree([1, 2, 3, 3, 4, 4, 4, 5, 6, 6, 5, 4, 4, 3, 2, 3])
        hg = list(T.height_groups())
        lt = list(T.map_labelling())
        bf = T.traverse_map()
        deg = DominantTree(T).degeneracy()
        for i in range(-7, 7):
            offset_tree = OrderedTree([t-i for t in T])
            self.assertSequenceEqual(hg, list(offset_tree.height_groups()))
            self.assertSequenceEqual(lt, list(offset_tree.map_labelling()))
            self.assertEqual(bf, offset_tree.traverse_map())
            self.assertEqual(deg, DominantTree(offset_tree).degeneracy())
