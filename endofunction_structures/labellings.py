#!/usr/bin/env python
# Copyright (C) 2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.

import itertools

from . import counts
from . import multiset
from . import necklaces
from . import rootedtrees
from . import endofunctions
from . import productrange


def _equipartitions(S, b):
    n = len(S)
    if b == 1 or n == 1:
        yield [frozenset(S)]
    else:
        marked_el = (S.pop(), )
        for first_combo in itertools.combinations(S, n//b-1):
            for remaining_combos in _equipartitions(S - set(first_combo), b-1):
                yield [frozenset(marked_el + first_combo)] + remaining_combos


def equipartitions(S, b):
    """Evenly split a set of items into unordered bins of unordered elements"""

    S = set(S)
    if len(S) % b:
        raise ValueError("items must divide evenly")
    for division in _equipartitions(S, b):
        yield frozenset(division)


def equipartition_count(n, b):
    """The total number of ways of evenly dividing a set S with n elements
    into b parts is n!/b!/(n/b)!**b which we can see as follows:

    Take all the permutations of S of which there are n!. We divide them
    into subsequences of length b. If we then disregard ordering each
    selection of subsequences will appear b! times. Each subsequence in
    each permutation of subsequences has (n/b)! representations, and there
    are b independent bins in each selection.

    Each combination of combinations will thus have (n/b)!**b * b! distinct
    representations. """

    return counts.factorial(n)//(counts.factorial(b)*counts.factorial(n//b)**b)


def _ordered_partitions(S, partition):
    if len(partition) == 1:
        yield [tuple(S)]
    else:
        for first in itertools.combinations(S, partition[0]):
            for remaining in _ordered_partitions(S-set(first), partition[1:]):
                yield [first] + remaining


def ordered_partitions(partition, S=None):
    """Enumerate ordered partitions of a set; i.e. order of the elements in
    each bin does not matter, but if the same bin is found in two different
    locations, it is a different ordered partition. Bin sizes are fixed and
    ordered according to partition."""
    partition = list(partition)
    if S is None:
        S = range(sum(partition))
    elif isinstance(S, int):
        S = range(S)
    S = set(S)
    if not len(S) == sum(partition):
        raise ValueError("partition must sum to size of set")
    for p in _ordered_partitions(S, partition):
        yield tuple(frozenset(s) for s in p)


def ordered_partition_count(partition, n=None):
    """Number of ordered combinations into the given partition. """
    return multinomial_coefficient(partition, n)


def _set_partitions(S, partition):
    lengths, mults = multiset.Multiset(partition).sort_split()
    # clm[i] is the number of nodes situated in some bin of size l[i].
    for odiv in _ordered_partitions(S, [l*m for l, m in zip(lengths, mults)]):
        strand = []
        for m, c in zip(mults, odiv):
            strand.append(_equipartitions(set(c), m))
        for bundle in itertools.product(*strand):
            yield itertools.chain.from_iterable(bundle)


def set_partitions(partition, S=None):
    """Unordered allocations of a set amongst a partition of bin sizes."""
    if S is None:
        S = range(sum(partition))
    elif isinstance(S, int):
        S = range(S)
    else:
        S = set(S)

    for subset in itertools.combinations(S, sum(partition)):
        for p in _set_partitions(set(subset), partition):
            yield frozenset(frozenset(s) for s in p)


def set_partition_count(partition, n=None):
    """The total number of ways of partitioning S with n elements into a given
    combination of bin sizes [l1, l2, ..., lk] with multiplicities [m1, m2,
    ..., mk] is given by n!/(l1!^m1 * m1!)/(l2!^m2 * m2!)/.../(lk!^mk * mk!),
    which may be seen as follows:

    List all permutations of S of which there are n!. Order the partition
    arbitrarily, and set division markers in each permutation at those
    locations. The number of appearances of each group of cycles of the same
    length is covered above. Their product is the number of combinations.

    Alternatively it is the cycle index divided by the factorial of one less
    than each cycle length, including multiplicity, since here permutation
    order does not matter. """

    partition = multiset.Multiset(partition)
    if n is None:
        n = sum(partition)
    count = counts.factorial(n)
    for l, m in zip(*partition.split()):
        count //= counts.factorial(l)**m * counts.factorial(m)
    return count


def _cycle_permutations(cycle):
    """Given a set of elements, a representative of each cyclic permutation of
    those elements."""
    cycle = set(cycle)
    start = min(cycle)
    cycle.remove(start)
    for p in itertools.permutations(cycle):
        yield necklaces.Necklace((start, ) + p, preordered=True)


def cycle_labellings(partition, S=None):
    """Given a conjugacy class of symmetric functions find all ways to label
    the cycle using the input set."""
    for upd in set_partitions(partition, S):
        for cycle_group in itertools.product(*map(_cycle_permutations, upd)):
            yield frozenset(cycle_group)


def cycle_index(partition, n=None):
    """Found by multiplying the set partition count by the product of the
    number of permutations of each cycle."""
    partition = multiset.Multiset(partition)
    if n is None:
        n = sum(partition)
    count = counts.factorial(n)
    for l, m in zip(*partition.split()):
        count //= l**m * counts.factorial(m)
    return count


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
    per se, as long as it is consistent for any suffix starting with that
    combination."""
    n = len(tree)
    bin_widths, translation_sequence = translation_keys(tree)
    func = [0] * n
    for combo in _ordered_partitions(set(range(n)), bin_widths):
        c = productrange.flatten(combo)
        for i in range(n):
            func[c[i]] = c[translation_sequence[i]]
        yield endofunctions.Endofunction(func)
