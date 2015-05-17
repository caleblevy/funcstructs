import unittest
import math

from PADS import IntegerPartitions

from .. import functions, multiset

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
        for n, count in enumerate(self.A000081, start=1):
            self.assertEqual(count, len(set(TreeEnumerator(n))))
            self.assertEqual(count, TreeEnumerator(n).cardinality)

    def test_forest_counts(self):
        """Check len(ForestEnumerator(N))==A000081(N+1)"""
        for n, count in enumerate(self.A000081[1:], start=1):
            intforests = set(ForestEnumerator(n))
            intforestcount = ForestEnumerator(n).cardinality
            pforests = set()
            pforestcount = 0
            for part in IntegerPartitions.partitions(n):
                pforests.update(PartitionForests(part))
                pforestcount += PartitionForests(part).cardinality
            self.assertEqual(count, len(intforests))
            self.assertEqual(count, len(pforests))
            self.assertEqual(count, intforestcount)
            self.assertEqual(count, pforestcount)
            self.assertEqual(intforests, pforests)

    def test_forest_elements(self):
        """spot check enumerated forests for some elements"""
        n = 9
        forests = set(ForestEnumerator(9))
        t1 = multiset.Multiset([DominantTree(range(n))])
        t2 = multiset.Multiset([
            DominantTree(range(n//2)),
            DominantTree(range(n-n//2))
        ])
        t3 = multiset.Multiset([DominantTree(iter([0]))]*n)
        nt1 = multiset.Multiset([DominantTree(range(n-1))])
        nt2 = multiset.Multiset([DominantTree(range(n+1))])
        n3 = DominantTree(range(n-1))
        nf4 = multiset.Multiset([OrderedTree(range(n))])
        n5 = multiset.Multiset(DominantTree(range(1, n+1)))
        for t in [t1, t2, t3]:
            self.assertIn(t, forests)
        for nt in [nt1, nt2, n3, nf4, n5]:
            self.assertNotIn(nt, forests)

    def test_labelling_counts(self):
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


class RootedTreeTests(unittest.TestCase):

    L1 = [1, 2, 3, 4, 5, 5, 4, 5, 5, 2, 3, 4, 5, 5, 4, 5, 5]
    L2 = range(1, 5)
    L3 = [1, 2, 2, 3, 2, 3, 4, 2, 3, 4, 5]
    R = RootedTree([
        RootedTree(),
        RootedTree(),
        RootedTree([
            RootedTree()
        ])
    ])

    def test_str(self):
        """Ensure Unordered trees are properly formatted."""
        T = RootedTree.from_levels(self.L1)
        T2 = RootedTree.from_levels(self.L2)
        T3 = RootedTree.from_levels(self.L3)
        self.assertEqual(str(T), "RootedTree({{{{{}^2}^2}}^2})")
        self.assertEqual(str(T2), "RootedTree({{{{}}}})")
        # Test correctness of dominance ordering
        self.assertEqual(str(T3), "RootedTree({{{{{}}}}, {{{}}}, {{}}, {}})")

    def test_len(self):
        """Test len(RootedTree) returns correct number of nodes"""
        for l in [self.L1, self.L2, self.L3]:
            self.assertEqual(len(l), len(RootedTree.from_levels(l)))
        self.assertEqual(5, len(self.R))

    def test_repr(self):
        """Test repr(Tree) == Tree for various trees."""
        for rt in map(RootedTree.from_levels, [self.L1, self.L2, self.L3]):
            self.assertEqual(rt, eval(repr(rt)))
        self.assertEqual(self.R, eval(repr(self.R)))

    def test_ordered_form(self):
        """Test conversion between rooted and unordered trees is seamless."""
        for l in [self.L1, self.L2, self.L3]:
            self.assertEqual(
                DominantTree(l),
                RootedTree.from_levels(l).ordered_form()
            )


class OrderedTreeTests(unittest.TestCase):

    def test_constructor_checks(self):
        """Test level sequences must be in increments by 1 above the root"""
        error_trees = [
            (0, 0, 1, 2, 3),
            (0, -1, 0, 1),
            (0, 1, 2, 3, 5),
            (1, 2.1, 3.1),
            ('y', 'z'),
            (1, 2, 'y'),
            (1, 2, 1)
        ]
        for et in error_trees:
            with self.assertRaises((ValueError, TypeError)):
                OrderedTree(et)
            with self.assertRaises((TypeError, IndexError, KeyError)):
                DominantTree(et)

    def test_dominance_ordering(self):
        """Test DominantTree produces dominant ordering"""
        self.assertSequenceEqual(
            [0, 1, 2, 3, 4, 1, 2, 3, 1, 2, 1],
            DominantTree([1, 2, 2, 3, 2, 3, 4, 2, 3, 4, 5])
        )

    def test_traverse_map(self):
        """Test the bracket representation of these rooted trees."""
        trees = [
            OrderedTree([0, 1, 2, 3, 4, 5, 3, 1, 2, 3]),
            OrderedTree([0, 1, 2, 3, 4, 5, 3, 1, 2, 2]),
            OrderedTree([0, 1, 2, 3, 4, 4, 4, 4, 4, 1]),
            # Test different orderings
            OrderedTree([0, 1, 1, 2, 1, 2, 3, 1, 2, 3]),
            OrderedTree([0, 1, 2, 3, 1, 2, 3, 1, 2, 1])
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

    def test_from_func(self):
        """Tests attached tree nodes and canonical_treeorder in one go."""
        for n in range(1, 10):
            for tree in TreeEnumerator(n):
                treefunc = functions.Endofunction.from_levels(tree)
                rtreefunc = functions.randconj(treefunc)
                self.assertEqual(tree, DominantTree.from_func(rtreefunc))
        # Make sure non-tree structures are caught
        with self.assertRaises(ValueError):
            OrderedTree.from_func(functions.rangefunc(range(10)))

    def test_breadth_first_traversal(self):
        """Test nodes are grouped correctly by their height"""
        T = OrderedTree([0, 1, 2, 2, 3, 3, 3, 4, 5, 5, 4, 3, 3, 2, 1, 2])
        bft = [0, 1, 14, 2, 3, 13, 15, 4, 5, 6, 11, 12, 7, 10, 8, 9]
        lp = T[0]
        for reference, computed in zip(bft, T.breadth_first_traversal()):
            self.assertEqual(reference, computed)
            self.assertGreaterEqual(T[computed], T[lp])
            lp = computed

    def test_height_independence(self):
        """Check that tree methods are unaffected by root height"""
        T = OrderedTree([1, 2, 3, 3, 4, 4, 4, 5, 6, 6, 5, 4, 4, 3, 2, 3])
        bft = list(T.breadth_first_traversal())
        ml = list(T.map_labelling())
        tm = T.traverse_map()
        d = DominantTree(T).degeneracy()
        rt = RootedTree.from_levels(T)
        for i in range(-7, 7):
            ot = OrderedTree([t-i for t in T])
            self.assertSequenceEqual(bft, list(ot.breadth_first_traversal()))
            self.assertSequenceEqual(ml, list(ot.map_labelling()))
            self.assertEqual(tm, ot.traverse_map())
            self.assertEqual(d, DominantTree(ot).degeneracy())
            self.assertEqual(rt, RootedTree.from_levels(ot))
