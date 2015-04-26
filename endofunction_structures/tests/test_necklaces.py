import unittest

from PADS import Lyndon

from endofunction_structures import factorization

from endofunction_structures.necklaces import (
    periodicity,
    Necklace,
    FixedContentNecklaces
)


class PeriodicityTest(unittest.TestCase):

    def test_periodicities(self):
        """Test periodicities of various lists"""
        periods = []
        lists = []
        N = 20
        for n in range(1, N+1):
            for d in factorization.divisors(n):
                periods.append(d)
                lists.append(([0]+[1]*(d-1))*(n//d))
        t1 = [(1, 2), ]*3+[(1, 1)]
        t2 = t1*3 + [(1, 4, 3)]*3 + [(1, )]
        t3 = t2*2 + [(2, )]*3 + [(1, 4, 3)]
        t4 = t3*3 + [(3, )]*3+[(1, 2)]
        lists.append(t4*4)
        periods.append(112)
        lists.extend([
            [(1, 2), (1, 2)],
            [(1, 2), (1, )],
            [(1, 2), (1, ), (1, 2), (1, ), (1, )],
            [(1, 2), (1, ), (1, 2), (1, ), (1, 2)]
        ])
        periods.extend([1, 2, 5, 5])
        for period, lst in zip(periods, lists):
            self.assertEqual(period, periodicity(lst))


class NecklaceTests(unittest.TestCase):

    def test_equality(self):
        """Check Necklace returns same output for different rotations of the
        input"""
        n = Necklace([1, 2, 3, 1, 2, 3])
        self.assertNotEqual(n, Necklace([1, 2, 3]))
        self.assertNotEqual(n, Necklace([1, 2, 3, 1, 2, 3, 1, 2, 3]))
        self.assertEqual(n, Necklace([3, 1, 2, 3, 1, 2]))
        self.assertEqual(n, Necklace(tuple([2, 3, 1, 2, 3, 1])))

    def test_hash(self):
        """Test that our hash is rotationally invariant"""
        self.assertEqual(hash(Necklace([1, 2, 3])), hash(Necklace([3, 1, 2])))

    def test_repr(self):
        n = Necklace([1, 2, 3, 1, 2, 3])
        self.assertEqual(n, eval(repr(n)))

    def test_keyability(self):
        dic = {}
        neck = Necklace([1, 2, 3, 1, 2, 3])
        dic[neck] = 1
        dic[neck] += 1
        self.assertEqual(1, len(dic))
        self.assertEqual(dic[neck], 2)

        neck2 = Necklace([3, 1, 2, 3, 1, 2])
        dic[neck2] += 1
        self.assertEqual(dic[neck], 3)
        self.assertEqual(1, len(dic))

        neck3 = Necklace([3, 2, 1, 3, 2, 1])
        with self.assertRaises(KeyError):
            dic[neck3] += 1

        dic[neck3] = 7
        self.assertEqual(2, len(dic))


class FixedContentNecklaceTests(unittest.TestCase):

    def test_from_partition(self):
        p1 = [3, 3, 2]
        p2 = [4, 4, 4, 3, 3, 2, 1, 1]
        p3 = [24, 36]
        p4 = [36, 24]
        b1 = [1]*3 + [2]*3 + [3]*2
        b2 = [1]*4 + [2]*4 + [3]*4 + [4]*3 + [5]*3 + [6]*2 + [7] + [8]
        b3 = [1]*24 + [2]*36
        b4 = [1]*36 + [2]*24  # test that order matters
        for b, p in zip([b1, b2, b3, b4], [p1, p2, p3, p4]):
            self.assertEqual(
                FixedContentNecklaces(b),
                FixedContentNecklaces.from_partition(p)
            )

    def test_total_counts(self):
        """Verify the count_by_period method agrees with Sage's totals."""
        partitions = [[3, 3, 2], [4, 4, 4, 3, 3, 2, 1, 1], [24, 36]]
        cardinalities = [70, 51330759480000, 600873126148801]
        for c, p in zip(cardinalities, partitions):
            nc = FixedContentNecklaces.from_partition(p).cardinality()
            self.assertEqual(c, nc)

    def test_enumeration_counts(self):
        """Test necklace counts for various bead sets."""
        beadsets = [[4, 4, 5, 5, 2, 2, 2, 2, 2, 2, 6, 6],
                    [4, 4, 5, 5, 2, 2, 2, 2, 2, 2, 6, 6, 6], [0]]
        for beadset in beadsets:
            count = 0
            necks = set()
            for necklace in FixedContentNecklaces(beadset):
                count += 1
                necks.add(necklace)
                necks.add(necklace)
            self.assertEqual(len(necks), count)

    def test_enumeration_period_counts(self):
        """Test distribution of periods of enumerated necklaces."""
        necks = FixedContentNecklaces.from_partition([6, 12])
        counts_by_period = necks.count_by_period()
        baseperiod = 3
        self.assertEqual(1038, sum(counts_by_period))
        for necklace in necks:
            counts_by_period[necklace.period//baseperiod] -= 1
        for count in counts_by_period:
            self.assertEqual(0, count)

    def test_ordering(self):
        necks = FixedContentNecklaces([1]*1 + [2]*2 + [3]*3)
        for necklace in necks:
            necklace = list(necklace)
            normalized_necklace = Lyndon.SmallestRotation(necklace)
            self.assertSequenceEqual(normalized_necklace, necklace)

    def test_keyability(self):
        dic = dict()
        a = FixedContentNecklaces([1, 1, 1, 2, 3])
        dic[a] = 1
        dic[FixedContentNecklaces([3, 1, 1, 2, 1])] = 2
        self.assertEqual(len(dic), 1)
        set(a)
        dic[a] += 1
        self.assertEqual(len(dic), 1)
        dic[FixedContentNecklaces([4, 4, 3, 2, 1])] = 7
        self.assertEqual(len(dic), 2)
