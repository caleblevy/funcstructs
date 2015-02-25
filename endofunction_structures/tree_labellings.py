#!/usr/bin/env python
# Copyright (C) 2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.

import math
import itertools
import unittest

from . import multiset
from . import rootedtrees
from . import productrange
from . import labellings
from . import endofunctions


def branch_inds(tree):
    """Return the grafting points of tree's main sub branches in order."""
    inds = []
    for i, node in enumerate(tree):
        if node == tree[0]+1:
            inds.append(i)
    return inds


def branch_groups(tree):
    """Yield, in order, tree's unique branches, and all nodes to which an
    instance of that branch is attached."""
    branches, mults = multiset.Multiset(tree.branches()).sort_split()
    branches = iter(branches[::-1])
    mults.reverse()
    indset = branch_inds(tree)[::-1]
    for m in mults:
        inds = []
        for _ in range(m):
            inds.append(indset.pop())
        yield next(branches), inds


def label_groups(tree):
    """ Order in which we label and group the nodes of the rooted tree. """
    if tree[0] == 1:
        yield [0]
    for subtree, inds in branch_groups(tree):
        yield inds
        for ind in inds:
            for indseq in label_groups(subtree):
                yield [i + ind for i in indseq]


def translation_keys(tree):
    """Given a combination of nodes from label groups, output keys with which
    to translate each combination into an endofunction."""
    ind_groups = list(label_groups(tree))
    bin_widths = list(map(len, ind_groups))
    indperm = endofunctions.SymmetricFunction(productrange.flatten(ind_groups))
    translation_sequence = indperm.conj(endofunctions.Endofunction(tree))
    return bin_widths, translation_sequence


def tree_labellings(tree):
    """Constant amortized time enumeration of every endofunction whose
    structure is described by the given tree. In many cases it may be much more
    efficient to use itertools.permutations (since they are at C speed) and may
    even be true in the amortized sense (since there are provably on average
    O(n!) labellings of a tree).

    Still, it is constant time per tree (really per node per tree), and its
    here for completeness sake.

    Note that order of the elements in a given combination bin does not matter
    PER SE, as long as it is consistant for any suffix with starting with that
    combination."""
    n = len(tree)
    bin_widths, translation_sequence = translation_keys(tree)
    func = [0] * n
    for combo in labellings._ordered_partitions(set(range(n)), bin_widths):
        c = productrange.flatten(combo)
        for i in range(n):
            func[c[i]] = c[translation_sequence[i]]
        yield endofunctions.Endofunction(func)


class TreeLabelTests(unittest.TestCase):

    trees = [
        rootedtrees.DominantTree([1, 2, 3, 3, 2, 3, 3, 2]),
        rootedtrees.DominantTree([1, 2, 3, 3, 2, 3, 3, 4, 5])
    ]

    def test_tree_label_count(self):
        """Ensure each tree has the correct number of representations"""
        for tree in self.trees:
            self.assertEqual(
                math.factorial(len(tree))//tree.degeneracy(),
                len(set(tree_labellings(tree)))
            )

    def test_trees_are_equivalent(self):
        """Ensure each endofunction is a representation of the original."""
        for tree in self.trees:
            for f in itertools.islice(tree_labellings(tree), 5040):
                self.assertEqual(tree, f.tree_form())


if __name__ == '__main__':
    unittest.main()
