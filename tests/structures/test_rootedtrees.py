import unittest
import math

from PADS import IntegerPartitions

from funcstructs.structures import functions, multiset

from funcstructs.structures.rootedtrees import (
    RootedTree,
    LevelSequence,
    DominantSequence,
    TreeEnumerator,
)


class TreeEnumerationTests(unittest.TestCase):
    A000081 = [1, 1, 2, 4, 9, 20, 48, 115, 286]

    def test_tree_counts(self):
        """OEIS A000081: number of unlabelled rooted trees on N nodes."""
        with self.assertRaises(ValueError):
            a = TreeEnumerator(0)  # Trees must have elements
        for n, count in enumerate(self.A000081, start=1):
            self.assertEqual(count, len(set(TreeEnumerator(n))))
            self.assertEqual(count, TreeEnumerator(n).cardinality())

    def test_canonical(self):
        """Ensure the implementation correctly enumerates DominantSequences."""
        for tree in TreeEnumerator(9):
            self.assertEqual(list(DominantSequence(tree)), list(tree))

    def test_labelling_counts(self):
        """OEIS A000169: n**(n-1) == number of rooted trees on n nodes."""
        for n in range(1, len(self.A000081)):
            ordered_count = 0
            rooted_count = 0
            nfac = math.factorial(n)
            for tree in TreeEnumerator(n):
                ordered_count += nfac//tree.degeneracy()
                rooted_count += nfac//RootedTree(tree).degeneracy()
            self.assertEqual(n**(n-1), ordered_count)
            self.assertEqual(n**(n-1), rooted_count)

    def test_tree_elements(self):
        """spot check enumerated trees for some elements"""
        trees = set(TreeEnumerator(9))
        self.assertIn(DominantSequence(range(9)), trees)
        self.assertIn(DominantSequence([0, 1, 2, 3, 4, 5, 1, 2, 3]), trees)
        self.assertIn(DominantSequence([0]+[1]*8), trees)
        # Check wrong size
        self.assertNotIn(DominantSequence(range(8)), trees)
        self.assertNotIn(DominantSequence(range(10)), trees)
        # Check non-canonical
        self.assertNotIn(LevelSequence([0, 1, 2, 3, 1, 2, 3, 4, 5]), trees)
        # Check for random crap
        self.assertNotIn(("a", "b", "c"), trees)
        self.assertNotIn("xyz", trees)


class RootedTreeTests(unittest.TestCase):

    L1 = LevelSequence([0, 1, 2, 3, 4, 4, 3, 4, 4, 1, 2, 3, 4, 4, 3, 4, 4])
    L2 = LevelSequence(range(4))
    L3 = LevelSequence([0, 1, 1, 2, 1, 2, 3, 1, 2, 3, 4])
    R = RootedTree([
        RootedTree(),
        RootedTree(),
        RootedTree([
            RootedTree()
        ])
    ])

    def test_str(self):
        """Ensure Unordered trees are properly formatted."""
        T = RootedTree(self.L1)
        T2 = RootedTree(self.L2)
        T3 = RootedTree(self.L3)
        self.assertEqual(str(T), "RootedTree({{{{{}^2}^2}}^2})")
        self.assertEqual(str(T2), "RootedTree({{{{}}}})")
        # Test correctness of dominance ordering
        self.assertEqual(str(T3), "RootedTree({{{{{}}}}, {{{}}}, {{}}, {}})")

    def test_len(self):
        """Test len(RootedTree) returns correct number of nodes"""
        for l in [self.L1, self.L2, self.L3]:
            self.assertEqual(len(l), len(RootedTree(l)))
        self.assertEqual(5, len(self.R))

    def test_repr(self):
        """Test repr(Tree) == Tree for various trees."""
        for rt in map(RootedTree, [self.L1, self.L2, self.L3]):
            self.assertEqual(rt, eval(repr(rt)))
        self.assertEqual(self.R, eval(repr(self.R)))

    def test_ordered_form(self):
        """Test conversion between rooted and unordered trees is seamless."""
        for l in [self.L1, self.L2, self.L3]:
            self.assertEqual(
                DominantSequence(l),
                RootedTree(l).ordered_form()
            )


class LevelSequenceTests(unittest.TestCase):

    def test_constructor(self):
        """Ensure any iterator over a valid level sequence returns a tree"""
        self.assertEqual(LevelSequence([0, 1]), LevelSequence(iter([0, 1])))
        self.assertEqual(LevelSequence([0, 1]), LevelSequence(tuple([0, 1])))

    def test_constructor_checks(self):
        """Test level sequences must be in increments by 1 above the root"""
        error_trees = [
            (0, 0, 1, 2, 3),  # multiple roots in front
            (0, -1, 0, 1),  # no negatives
            (0, 1, 2, -1),  # no negatives
            (0, 1, 2, 3, 5),  # height jump more than 2
            (0, 1, 2, 3, 4, 2, 4),  # height jump to node already seen
            (0, 1.1, 2.1),  # floating point differences
            ('y', 'z'),  # Tests for random stuff
            (0, 1, 'y'),  # letter at ends
            (0, 2, 0),  # height jump at beginning
            (1, 2, 3),  # must begin at 0
            (1, ),  # even in degenerate cases
            (-1, ),
            (),  # must have an element
        ]
        for et in error_trees:
            with self.assertRaises((ValueError, TypeError)):
                LevelSequence(et)
            with self.assertRaises((TypeError, ValueError, LookupError)):
                DominantSequence(et)

    def test_dominance_ordering(self):
        """Test DominantSequence produces dominant ordering"""
        self.assertSequenceEqual(
            [0, 1, 2, 3, 4, 1, 2, 3, 1, 2, 1],
            DominantSequence([0, 1, 1, 2, 1, 2, 3, 1, 2, 3, 4])
        )

    def test_traverse_map(self):
        """Test the bracket representation of these rooted trees."""
        trees = [
            LevelSequence([0, 1, 2, 3, 4, 5, 3, 1, 2, 3]),
            LevelSequence([0, 1, 2, 3, 4, 5, 3, 1, 2, 2]),
            LevelSequence([0, 1, 2, 3, 4, 4, 4, 4, 4, 1]),
            # Test different orderings
            LevelSequence([0, 1, 1, 2, 1, 2, 3, 1, 2, 3]),
            LevelSequence([0, 1, 2, 3, 1, 2, 3, 1, 2, 1])
        ]
        nestedforms = (
            [[[[[[]]], []]], [[[]]]],
            [[[[[[]]], []]], [[], []]],
            [[[[[], [], [], [], []]]], []],
            [[], [[]], [[[]]], [[[]]]],
            [[[[]]], [[[]]], [[]], []]
        )
        for tree, nest in zip(trees, nestedforms):
            self.assertSequenceEqual(nest, tree.traverse_map())

    def test_map_labelling(self):
        """Check that a functions from tree.map_labelling represent the tree"""
        tree = LevelSequence([0, 1, 2, 3, 3, 3, 2, 3, 3, 1, 2, 2, 1, 2])
        func = functions.rangefunc([0, 0, 1, 2, 2, 2, 1, 6, 6, 0, 9, 9, 0, 12])
        self.assertEqual(func, functions.rangefunc(tree.map_labelling()))

    def test_from_func(self):
        """Tests attached tree nodes and canonical_treeorder in one go."""
        for n in range(1, 10):
            for tree in TreeEnumerator(n):
                treefunc = functions.rangefunc(tree.map_labelling())
                rtreefunc = functions.randconj(treefunc)
                self.assertEqual(tree, DominantSequence.from_func(rtreefunc))
        # Make sure non-tree structures are caught
        with self.assertRaises(ValueError):
            LevelSequence.from_func(functions.rangefunc(range(10)))

    def test_breadth_first_traversal(self):
        """Test nodes are grouped correctly by their height"""
        T = LevelSequence([0, 1, 2, 2, 3, 3, 3, 4, 5, 5, 4, 3, 3, 2, 1, 2])
        bft = [0, 1, 14, 2, 3, 13, 15, 4, 5, 6, 11, 12, 7, 10, 8, 9]
        lp = T[0]
        for reference, computed in zip(bft, T.breadth_first_traversal()):
            self.assertEqual(reference, computed)
            self.assertGreaterEqual(T[computed], T[lp])
            lp = computed
