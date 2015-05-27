import unittest
from math import factorial

from ..functions import (
    Function, Bijection, Endofunction, SymmetricFunction,
    rangefunc, rangeperm, randfunc, randperm, randconj,
    Mappings, Isomorphisms, TransformationMonoid, SymmetricGroup
)


class FunctionTests(unittest.TestCase):

    abcfunc = Function({'a': 1, 'b': 1, 'c': 1})

    def test_function_constructor(self):
        """Test the constructor accepts and rejects appropriate input"""
        f = self.abcfunc
        self.assertEqual(f, Function(f.items()))
        self.assertEqual(f, Function.fromkeys("abc", 1))
        self.assertEqual(f, Function(f))
        self.assertEqual(f, Function(a=1, b=1, c=1))
        with self.assertRaises(TypeError):
            Function({0: 'a', 1: 'b', 2: ['c', 'd']})

    def test_domain(self):
        self.assertEqual(self.abcfunc.domain, frozenset("abc"))

    def test_image(self):
        self.assertEqual(self.abcfunc.image, frozenset({1}))

    def test_preimage(self):
        self.assertEqual({1: frozenset("abc")}, dict(self.abcfunc.preimage))


class EndofunctionTests(unittest.TestCase):

    # Imagepath Tests

    def test_iterate(self):
        """Test Endofunctions can be properly iterated"""
        sigma = rangefunc([1, 2, 3, 0, 5, 6, 4])  # Perm (0,1,2,3)(4,5,6)
        identity = rangefunc(range(7))
        for I in range(1, 11):  # Order of cycle is 12
            self.assertNotEqual(identity.cycles, (sigma**I).cycles)
        self.assertEqual(identity.cycles, (sigma**12).cycles)

    def test_imagepath(self):
        """Check various special and degenerate cases, with right index"""
        self.assertSequenceEqual([1], rangefunc([0]).imagepath)
        self.assertSequenceEqual([1], rangefunc([0, 0]).imagepath)
        self.assertSequenceEqual([1], rangefunc([1, 1]).imagepath)
        self.assertSequenceEqual([2], rangefunc([0, 1]).imagepath)
        self.assertSequenceEqual([2], rangefunc([1, 0]).imagepath)
        node_count = [2, 3, 5, 15]
        for n in node_count:
            tower = rangefunc([0] + list(range(n-1)))
            cycle = rangefunc([n-1] + list(range(n-1)))
            fixed = rangefunc(list(range(n)))
            degen = rangefunc([0]*n)
            self.assertSequenceEqual(list(range(n)[:0:-1]), tower.imagepath)
            self.assertSequenceEqual([n]*(n-1), cycle.imagepath)
            self.assertSequenceEqual([n]*(n-1), fixed.imagepath)
            self.assertSequenceEqual([1]*(n-1), degen.imagepath)

    # Cycle tests

    funcs = [
        rangefunc([1, 0]),
        rangefunc([9, 5, 7, 6, 2, 0, 9, 5, 7, 6, 2]),
        rangefunc([7, 2, 2, 3, 4, 3, 9, 2, 2, 10, 10, 11, 12, 5])
    ]
    funcs += list([randfunc(20) for _ in range(100)])
    funcs += list(TransformationMonoid(1))
    funcs += list(TransformationMonoid(3))
    funcs += list(TransformationMonoid(4))

    def test_cycles_are_cyclic(self):
        """Make sure funccylces actually returns cycles."""
        for f in self.funcs:
            for cycle in f.cycles:
                for ind, el in enumerate(cycle):
                    self.assertEqual(cycle[(ind+1) % len(cycle)], f[el])

    def test_cycles_are_unique(self):
        """Ensure funccycles returns no duplicates."""
        for f in self.funcs:
            self.assertEqual(len(f.cycles), len(set(f.cycles)))

    def test_cycles_are_complete(self):
        """Ensure funccycles returns every cycle."""
        for f in self.funcs:
            self.assertEqual(f.imagepath[-1], len(f.limitset))

    def test_acyclic_ancestors_are_not_cyclic(self):
        """Make sure attached_treenodes returns nodes not in cycles."""
        for f in self.funcs:
            for _, invim in f.acyclic_ancestors.items():
                for x in invim:
                    self.assertNotIn(x, f.limitset)

    # Permutation Tests

    def test_inverse(self):
        """Test compose(inv(perm), perm) == perm"""
        permlist = []
        for n in range(1, 10):
            for _ in range(1, 10*n):
                permlist.append(randperm(n))

        for perm in permlist:
            e = rangeperm(range(len(perm)))
            self.assertSequenceEqual(e, perm * perm.inverse)
            self.assertSequenceEqual(e, perm.inverse * perm)
            self.assertSequenceEqual(perm, perm.inverse.inverse)

    def test_conjugation(self):
        """Test that conjugation is invertible, with the obvious inverse."""
        for f in self.funcs:
            for _ in range(20):
                perm = randperm(len(f))
                self.assertEqual(f, perm.inverse.conj(perm.conj(f)))


def _func_images(mspace):
    funcs = set()
    for func in mspace:
        x, f = func.sort_split()
        funcs.add(f)
    return funcs


class FunctionEnumeratorTests(unittest.TestCase):

    domranges = [((i, range(4)[:i]), (j, "abcd"[:j])) for i in range(5)
                 for j in range(5)]
    domranges += list(map(list, map(reversed, domranges)))

    def assertFuncCountsEqual(self, count, mspace):
        """Assert that various aspects of the counts are equal"""
        self.assertEqual(count, len(mspace))
        self.assertEqual(count, len(set(mspace)))
        self.assertEqual(count, len(_func_images(mspace)))

    def assertDomainsCorrect(self, mspace):
        """Assert that enumerated functions have correct domains and ranges."""
        for f in mspace:
            self.assertTrue(f.domain.issubset(mspace.domain))
            if hasattr(mspace, "codomain"):
                self.assertTrue(f.image.issubset(mspace.codomain))
            else:
                self.assertTrue(f.image.issubset(mspace.domain))

    def test_function_counts(self):
        """Check the number of mappings produced by function enumerators."""
        for (i, d), (j, c) in self.domranges:
            # test Function counts
            self.assertFuncCountsEqual(j**i, Mappings(d, c))
            if i == j:
                # test Bijection counts
                self.assertFuncCountsEqual(factorial(i), Isomorphisms(d, c))
                # test Endofunction counts
                self.assertFuncCountsEqual(i**i, TransformationMonoid(d))
                # test Permutation counts
                self.assertFuncCountsEqual(factorial(i), SymmetricGroup(d))
            else:
                # ensure there are no bijections between non-isomorphic sets
                with self.assertRaises(ValueError):
                    Isomorphisms(d, c)

    def test_function_domains(self):
        """Check that enumerated functions have correct domains and ranges."""
        for (_, d), (_, c) in self.domranges:
            # Check that Functions are correct
            self.assertDomainsCorrect(Mappings(d, c))
            if len(c) == len(d):
                self.assertDomainsCorrect(Isomorphisms(d, c))
                self.assertDomainsCorrect(TransformationMonoid(d))
                self.assertDomainsCorrect(SymmetricGroup(d))
