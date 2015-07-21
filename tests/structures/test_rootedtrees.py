import unittest
import math

from PADS import IntegerPartitions

from funcstructs.structures import functions, multiset

from funcstructs.structures.rootedtrees import (
    RootedTree,
    LevelSequence,
    DominantSequence,
    TreeEnumerator,
    forests
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

    def test_forest_elements(self):
        """spot check enumerated forests for some elements"""
        n = 9
        t1 = multiset.Multiset([DominantSequence(range(n))])
        t2 = multiset.Multiset([
            DominantSequence(range(n//2)),
            DominantSequence(range(n-n//2))
        ])
        t3 = multiset.Multiset([DominantSequence(iter([0]))]*n)
        nt1 = multiset.Multiset([DominantSequence(range(n-1))])
        nt2 = multiset.Multiset([DominantSequence(range(n+1))])
        n3 = DominantSequence(range(n-1))
        nf4 = multiset.Multiset([LevelSequence(range(n))])
        n5 = multiset.Multiset(DominantSequence(range(1, n+1)))
        f = set(forests(9))
        for t in [t1, t2, t3]:
            self.assertIn(t, f)
        for nt in [nt1, nt2, n3, nf4, n5]:
            self.assertNotIn(nt, f)


class RootedTreeTests(unittest.TestCase):

    L1 = LevelSequence([1, 2, 3, 4, 5, 5, 4, 5, 5, 2, 3, 4, 5, 5, 4, 5, 5])
    L2 = LevelSequence(range(1, 5))
    L3 = LevelSequence([1, 2, 2, 3, 2, 3, 4, 2, 3, 4, 5])
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

    def test_constructor_checks(self):
        """Test level sequences must be in increments by 1 above the root"""
        error_trees = [
            (0, 0, 1, 2, 3),
            (0, -1, 0, 1),
            (0, 1, 2, 3, 5),
            (0, 1, 2, 3, 4, 2, 4),
            (1, 2.1, 3.1),
            ('y', 'z'),
            (1, 2, 'y'),
            (1, 2, 1)
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
            DominantSequence([1, 2, 2, 3, 2, 3, 4, 2, 3, 4, 5])
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
        tree = LevelSequence([1, 2, 3, 4, 4, 4, 3, 4, 4, 2, 3, 3, 2, 3])
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

    def test_height_independence(self):
        """Check that tree methods are unaffected by root height"""
        T = LevelSequence([1, 2, 3, 3, 4, 4, 4, 5, 6, 6, 5, 4, 4, 3, 2, 3])
        bft = list(T.breadth_first_traversal())
        ml = list(T.map_labelling())
        tm = T.traverse_map()
        d = DominantSequence(T).degeneracy()
        rt = RootedTree(T)
        for i in range(-7, 7):
            ot = LevelSequence([t-i for t in T])
            self.assertSequenceEqual(bft, list(ot.breadth_first_traversal()))
            self.assertSequenceEqual(ml, list(ot.map_labelling()))
            self.assertEqual(tm, ot.traverse_map())
            self.assertEqual(d, DominantSequence(ot).degeneracy())
            self.assertEqual(rt, RootedTree(ot))
