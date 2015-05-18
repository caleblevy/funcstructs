import unittest

from .. import frozendict


class FrozendictTests(unittest.TestCase):

    class F(frozendict):
        pass

    a = {'a': 1, 'b': 2, 'c': 3}
    b = frozendict({'a': 1, 'b': 2, 'c': 3})
    c = F(b)
    e = frozendict({1: [1, 2, 3], 2: (1, 2, 3)})
    f = frozendict({b: 14, 1: 15})
    dicts = [a, b, c, e, f]

    def test_constructors(self):
        """Test frozendict works with usual constructors"""
        kwargs = {'c': 3, 'd': 4, 'e': 5}
        for fdclass in [frozendict, self.F]:
            self.assertEqual(
                {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5},
                dict(fdclass(a=1, b=2, **kwargs))
            )
            self.assertEqual(
                {1: 1, 2: 2, 3: 3, 4: 4, 5: 5},
                dict(fdclass(enumerate(range(1, 6), start=1)))
            )
            self.assertEqual(
                fdclass.fromkeys([1, 2, 3], None),
                fdclass({1: None, 2: None, 3: None})
            )

    def test_equality(self):
        """Test different dicts compare differently"""
        t = {'d': 1, 'e': 2, 'a': 3}
        others = [t, frozendict(t), self.F(t)]
        for i, d1 in enumerate(self.dicts):
            for j, d2 in enumerate(self.dicts):
                if i == j:
                    self.assertEqual(d1, d2)
                else:
                    self.assertNotEqual(d1, d2)
                if i < 3 and j < 3:
                    self.assertEqual(d2, d2.__class__(d1))
                    self.assertNotEqual(d1, others[j])

    def test_immutability(self):
        """Test that all inherited mutating methods have been disabled."""
        for d in [self.b, self.c]:
            with self.assertRaises(TypeError):
                d['a'] += 1
            with self.assertRaises(TypeError):
                d['b'] = 2
            with self.assertRaises(TypeError):
                del d['b']
            with self.assertRaises(TypeError):
                d.clear()
            with self.assertRaises(TypeError):
                d.pop('a')
            with self.assertRaises(TypeError):
                d.popitem()
            with self.assertRaises(TypeError):
                d.setdefault('f', 1)
            with self.assertRaises(TypeError):
                d.update({'d': 4})
            self.assertEqual(d.__class__({'a': 1, 'b': 2, 'c': 3}), d)

    def test_repr(self):
        """Ensure fronzendicts evaluate to themselves"""
        for d in self.dicts:
            self.assertEqual(d, eval(repr(d), {d.__class__.__name__: type(d)}))

    def test_hashing(self):
        """Test that frozendicts with hashable keys are hashable"""
        dic = dict()
        dic[self.b] = 1
        dic[self.c] = 2
        self.assertEqual(2, len(dic))
        dic2 = {self.F({'b': 2, 'c': 3, 'a': 1}): 2, self.b: 1}
        self.assertEqual(dic, dic2)
        with self.assertRaises(TypeError):
            hash(self.e)
        dic2[self.c] -= 1
        self.assertEqual(set(dic2.values()), {1})
        self.assertEqual(set(dic), {self.b, self.c})
