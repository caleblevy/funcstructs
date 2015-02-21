import math
import itertools
import unittest

import multiset


def evenly_split_by_filtering(s, b):
    """Evenly split S into b parts. Very slow; for testing only."""
    S = multiset.Multiset(s)
    n = len(S)
    if not n == len(S):
        raise ValueError("We must split a set, not multiset")
    if n % b:
        raise ValueError("cannot divide evenly")
    ls = [n//b]*b
    for mpart in S.partitions():
        if [len(el) for el in mpart] == ls:
            yield frozenset(frozenset(m) for m in mpart)


def split_into_halves(items):
    """ Split a set into two; i.e. multiset partitions of items into two equal
    sized bins. """
    items = list(items)
    S = set(items)
    n = len(items)
    if n % 2:
        raise ValueError("needs an even number of items")
    tot = multiset.nCk(n, n//2)//2
    count = 0
    for p in itertools.combinations(items, n//2):
        count += 1
        if count > tot:
            break
        yield frozenset([frozenset(p), frozenset(S - set(p))])


def split_into_thirds(items):
    """Split a set into thirds; i.e. multiset partitions of items into three
    equally sized bins."""
    items = list(items)
    n = len(items)
    if n % 3:
        raise ValueError("items must be split into thirds")
    marked_el = items[0]
    items = items[1:]
    S = set(items)
    for first_combo in itertools.combinations(items, n//3-1):
        remaining_elements = sorted(list(S - set(first_combo)))
        for remaining_split in split_into_halves(remaining_elements):
            yield frozenset([frozenset((marked_el,)+first_combo)] + list(remaining_split))


class LabellingTests(unittest.TestCase):

    def test_splits(self):
        """Test sets are split evenly and identical to multiset partitions."""
        S = range(6)
        s1 = frozenset(split_into_halves(S))
        s2 = frozenset(evenly_split_by_filtering(range(6), 2))
        self.assertEqual(s2, s1)

        s3 = frozenset(split_into_thirds(S))
        s4 = frozenset(evenly_split_by_filtering(range(6), 3))
        self.assertEqual(s3, s4)

        P = range(9)
        p1 = frozenset(split_into_thirds(P))
        p2 = frozenset(evenly_split_by_filtering(P, 3))
        self.assertEqual(p1, p2)


if __name__ == '__main__':
    unittest.main()