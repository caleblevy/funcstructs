import unittest

from collections import Mapping


def split(items, sort=False, key=None, reverse=False):
    """Split an iterable into unzipped pairs."""
    if isinstance(items, Mapping):
        items = items.items()
        default = ((), ())
    else:
        default = ()
    if sort:
        items = sorted(items, key=key, reverse=reverse)
    unzipped = tuple(zip(*items))
    return unzipped if unzipped else default


class SplittingTests(unittest.TestCase):

    def test_dict_splitting(self):
        """Test that dicts are split in key-value lists."""
        from funcstructs import frozendict, Multiset, Bijection
        d1 = {'a': 1, 1: (), (1, 2): 'b', None: None, frozenset(): Multiset()}
        d2 = Bijection(d1)
        d3 = d2.inverse
        d4 = Multiset("(choice(ascii_lowercase) for _ in range(10))")
        for d in [d1, d2, d3, d4]:
            keys, values = split(d)
            for k, v in zip(keys, values):
                self.assertEqual(v, d[k])

    def test_iterable_splitting(self):
        """Test that split is the reverse of zip"""
        self.assertEqual(
            ((1, 4, 7), (2, 5, 8), (3, 5, 9)),
            split(((1, 2, 3), (4, 5, 6), (7, 8, 9)))
        )
