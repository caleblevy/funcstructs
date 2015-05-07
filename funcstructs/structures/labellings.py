"""Algorithms for enumerating all labellings of given unlabelled structures.

Caleb Levy, 2015.
"""

from itertools import combinations, permutations, product
from math import factorial

from .combinat import multinomial_coefficient as ordered_division_count
from .endofunctions import Endofunction, SymmetricFunction
from .multiset import Multiset
from .necklaces import Necklace
from .utils import flatten

__all__ = [
    "equipartitions", "equipartition_count",
    "ordered_divisions", "ordered_division_count",
    "set_partitions", "set_partition_count",
    "cycle_labellings", "cycle_index",
    "tree_labellings"
]


def _equipartitions(S, b):
    n = len(S)
    if b == 1 or n == 1:
        yield [tuple(S)]
    else:
        marked_el = (S.pop(), )
        for first in combinations(S, n//b-1):
            for remaining in _equipartitions(S.difference(first), b-1):
                yield [marked_el + first] + remaining


def equipartitions(S, b):
    """Partitions of S into b of equally sized unordered bins."""
    S = set(S)
    if len(S) % b:
        raise ValueError("items must divide evenly")
    for division in _equipartitions(S, b):
        yield frozenset(map(frozenset, division))


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

    return factorial(n) // (factorial(b) * factorial(n//b)**b)


def _ordered_divisions(S, part):
    if len(part) == 1:
        yield [tuple(S)]
    else:
        for first in combinations(S, part[0]):
            for remaining in _ordered_divisions(S.difference(first), part[1:]):
                yield [first] + remaining


def ordered_divisions(partition, S=None):
    """Enumerate ordered partitions of a set; i.e. order of the elements in
    each bin does not matter, but if the same bin is found in two different
    locations, it is a different ordered partition. Bin sizes are fixed and
    ordered according to partition."""
    partition = list(partition)
    if S is None:
        S = sum(partition)
    if isinstance(S, int):
        S = range(S)
    if not len(S) == sum(partition):
        raise ValueError("partition must sum to size of set")
    for p in _ordered_divisions(set(S), partition):
        yield tuple(map(frozenset, p))


def _set_partitions(S, partition):
    lengths, mults = Multiset(partition).sort_split()
    # clm[i] is the number of nodes situated in some bin of size l[i].
    for odiv in _ordered_divisions(S, [l*m for l, m in zip(lengths, mults)]):
        strand = []
        for m, c in zip(mults, odiv):
            strand.append(_equipartitions(set(c), m))
        for bundle in product(*strand):
            yield flatten(bundle)


def set_partitions(partition, S=None):
    """Unordered allocations of a set amongst a partition of bin sizes."""
    if S is None:
        S = sum(partition)
    if isinstance(S, int):
        S = range(S)
    for subset in combinations(S, sum(partition)):
        for p in _set_partitions(set(subset), partition):
            yield frozenset(map(frozenset, p))


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
    partition = Multiset(partition)
    if n is None:
        n = sum(partition)
    count = factorial(n)
    for l, m in zip(*partition.split()):
        count //= factorial(l)**m * factorial(m)
    return count


def _cycle_permutations(cycle):
    """Given a set of elements, a representative of each cyclic permutation of
    those elements."""
    cycle = set(cycle)
    start = min(cycle)
    cycle.remove(start)
    for p in permutations(cycle):
        # The cycles are necklaces: they start with the minimal element, and
        # all elements are unique, hence they are lexicographically minimal.
        yield Necklace((start, )+p, preordered=True)


def cycle_labellings(partition, S=None):
    """Enumerate cycles with cycle type partition and labels from S"""
    for upd in set_partitions(partition, S):
        for cycle_group in product(*map(_cycle_permutations, upd)):
            yield frozenset(cycle_group)


def cycle_index(partition, n=None):
    """Found by multiplying the set partition count by the product of the
    number of permutations of each cycle."""
    partition = Multiset(partition)
    if n is None:
        n = sum(partition)
    count = factorial(n)
    for l, m in zip(*partition.split()):
        count //= l**m * factorial(m)
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
    branches, mults = Multiset(tree.branches()).sort_split()
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
    if tree[0] == 0:
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
    translation_sequence = SymmetricFunction(flatten(ind_groups)).inverse.conj(
        Endofunction.from_levels(tree))
    return bin_widths, translation_sequence


def tree_labellings(tree):
    """ Constant amortized time enumeration of every endofunction whose
    structure is described by the given tree. In many cases it may be much more
    efficient to use itertools.permutations (since they are at C speed) and may
    even be true in the amortized sense (since there are provably on average
    O(n!) labellings of a tree).

    Still, it is constant time per tree (really per node per tree), and it's
    here for completeness sake.

    Note that order of the elements in a given combination bin does not matter
    per se, as long as it is consistent for any suffix starting with that
    combination."""
    n = len(tree)
    bin_widths, translation_sequence = translation_keys(tree)
    func = [0] * n
    for combo in _ordered_divisions(set(range(n)), bin_widths):
        c = list(flatten(combo))
        for i in range(n):
            func[c[i]] = c[translation_sequence[i]]
        yield Endofunction(func)
