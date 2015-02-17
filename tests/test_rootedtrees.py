import unittest
from endofunction_structures.rootedtrees import *
from endofunction_structures.endofunctions import Endofunction

class TreeTests(unittest.TestCase):

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
            self.assertEqual(count, len(TreeEnumerator(n+1)))

    def test_forest_counts(self):
        """Check len(ForestEnumerator(N))==A000081(N+1)"""
        for n, count in enumerate(self.A000081[1:]):
            forests = set()
            for forest in ForestEnumerator(n+1):
                forests.add(forest)
                forests.add(forest)
            self.assertEqual(self.A000081[n+1], len(forests))
            self.assertEqual(self.A000081[n+1], len(ForestEnumerator(n+1)))

    def test_partition_forest_counts(self):
        """Check alternate way of enumerating forests."""
        from PADS.IntegerPartitions import partitions
        for n, count in enumerate(self.A000081[1:]):
            forests = set()
            forest_count = 0
            for partition in partitions(n+1):
                forests.update(PartitionForests(partition))
                forest_count += len(PartitionForests(partition))
            self.assertEqual(self.A000081[n+1], len(forests))
            self.assertEqual(self.A000081[n+1], forest_count)

    def test_tree_degeneracy(self):
        """OEIS A000169: n**(n-1) == number of rooted trees on n nodes."""
        for n in range(1, len(self.A000081)):
            labelled_treecount = 0
            rooted_treecount = 0
            nfac = math.factorial(n)
            for tree in TreeEnumerator(n):
                labelled_treecount += nfac//tree.degeneracy()
                rooted_treecount += nfac//tree.unordered().degeneracy()
            self.assertEqual(n**(n-1), labelled_treecount)
            self.assertEqual(n**(n-1), rooted_treecount)

    # Basic method tests

    def test_rooted_tree_strings(self):
        T = unordered_tree([1, 2, 3, 4, 5, 5, 4, 5, 5, 2, 3, 4, 5, 5, 4, 5, 5])
        T2 = unordered_tree(range(1, 5))
        self.assertEqual(str(T), "RootedTree({{{{{}^2}^2}}^2})")
        self.assertEqual(str(T2), "RootedTree({{{{}}}})")

    def test_reprs(self):
        TreeSeqs = [[1, 2, 3, 4, 5, 5, 4, 5, 5, 2, 3, 4, 5, 5, 4, 5, 5],
                    [1, 2, 3, 4, 5, 4, 5, 5, 2, 3, 2, 3, 4, 4, 5, 6],
                    range(1, 5)]
        for seq in TreeSeqs:
            T_unordered = unordered_tree(seq)
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

    def test_equality(self):
        node_counts = [4, 5, 6, 10]
        enumerators = [TreeEnumerator, ForestEnumerator]
        for n in node_counts:
            for enum1 in enumerators:
                for m in node_counts:
                    for enum2 in enumerators:
                        if n == m and enum1 == enum2:
                            self.assertEqual(enum1(n), enum2(m))
                        else:
                            self.assertNotEqual(enum1(n), enum2(m))

    # Test conversion methods

    def test_bracket_form(self):
        """Test the bracket representation of these rooted trees."""
        trees = [
            OrderedTree([1, 2, 3, 4, 5, 6, 4, 2, 3, 4]),
            OrderedTree([1, 2, 3, 4, 5, 6, 4, 2, 3, 3]),
            OrderedTree([1, 2, 3, 4, 5, 5, 5, 5, 5, 2]),
        ]
        nestedforms = (
            [[[[[[]]], []]], [[[]]]],
            [[[[[[]]], []]], [[], []]],
            [[[[[], [], [], [], []]]], []]
        )
        for tree, nest in zip(trees, nestedforms):
            self.assertSequenceEqual(nest, tree.bracket_form())

    def test_from_treefunc(self):
        """Tests attached treenodes and canonical_treeorder in one go."""
        for n in range(1, 10):
            for tree in TreeEnumerator(n):
                treefunc = Endofunction.from_tree(tree)
                for _ in range(10):
                    rtreefunc = treefunc.randconj()
                    self.assertEqual(tree, DominantTree.from_func(rtreefunc))