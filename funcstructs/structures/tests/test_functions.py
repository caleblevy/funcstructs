import unittest
from math import factorial

from ..conjstructs import Funcstruct

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
        self.assertEqual({1: frozenset("abc")}, dict(self.abcfunc.preimage()))


class CompositionTests(unittest.TestCase):
    I = list(enumerate(range(10)))
    ids = [Function(I), Bijection(I), Endofunction(I), SymmetricFunction(I)]

    def test_composition_types(self):
        """Test the four type rules for function composition"""
        f, b, e, s = self.ids
        # test rule 1)
        self.assertEqual(f, f*f)
        self.assertEqual(b, b*b)
        self.assertEqual(e, e*e)
        self.assertEqual(s, s*s)
        # test rule 2)
        self.assertEqual(f, f*e)
        self.assertEqual(f, e*f)
        self.assertEqual(f, f*b)
        self.assertEqual(f, b*f)
        self.assertEqual(f, f*s)
        self.assertEqual(f, s*f)
        # test rule 3)
        self.assertEqual(e, e*s)
        self.assertEqual(e, s*e)
        self.assertEqual(b, b*s)
        self.assertEqual(b, s*b)
        # test rule 4)
        self.assertEqual(f, e*b)
        self.assertEqual(f, b*e)

    def test_conjugation_types(self):
        """Test that conjugate of an object is the original type"""
        _, b, _, s = self.ids
        for func in self.ids:
            self.assertEqual(func, b.conj(func))
            self.assertEqual(func, s.conj(func))

    def test_conjugation(self):
        """Test that conjugation works in the correct order"""
        # 0   1
        #  \ /
        #   2
        #  / \
        # 3<-4
        f = rangefunc([2, 2, 4, 2, 3])
        s = rangeperm([0, 1, 3, 4, 2])
        g = rangefunc([3, 3, 4, 2, 3])  # g = s*f*s**-1
        self.assertEqual(g, s.conj(f))
        self.assertNotEqual(g, s.inverse.conj(f))
        # Test that if function has cycle
        #    t=(a1, a2, ..., an)
        # then
        #    s.conj(t) = (s[a1], s[a2], ..., s[an])
        sigma = rangeperm([1, 2, 0, 4, 3])  # s = (0, 1, 2)(3, 4)
        tau = rangeperm([1, 2, 3, 4, 0])  # t = (0, 1, 2, 3, 4)
        sr = rangeperm([4, 2, 3, 1, 0])  # t*s*t^-1 = (1, 2, 3)(4, 0)
        sl = rangeperm([1, 4, 3, 2, 0])  # t^-1*s*t = (0, 1, 4)(2, 3)
        self.assertEqual(sr, tau.conj(sigma))
        self.assertEqual(sl, tau.inverse.conj(sigma))

    def test_domain_changing(self):
        """Test changing an endofunction's domain does not change structure"""
        f = Endofunction.fromkeys("abc", "a")
        b = Bijection(zip("abc", range(3)))
        self.assertEqual(f, b.inverse.conj(b.conj(f)))
        self.assertEqual(Funcstruct(f), Funcstruct(b.conj(f)))


class EndofunctionTests(unittest.TestCase):

    # Imagepath Tests

    def test_iterate(self):
        """Test Endofunctions can be properly iterated"""
        sigma = rangefunc([1, 2, 3, 0, 5, 6, 4])  # Perm (0,1,2,3)(4,5,6)
        identity = rangefunc(range(7))
        for I in range(1, 11):  # Order of cycle is 12
            self.assertNotEqual(identity.cycles(), (sigma**I).cycles())
        self.assertEqual(identity.cycles(), (sigma**12).cycles())

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
    cyclesets = [f.cycles() for f in funcs]
    limitsets = [f.limitset() for f in funcs]

    def test_cycles_are_cyclic(self):
        """Make sure funccylces actually returns cycles."""
        for f, cycles in zip(self.funcs, self.cyclesets):
            for cycle in cycles:
                for ind, el in enumerate(cycle):
                    self.assertEqual(cycle[(ind+1) % len(cycle)], f[el])

    def test_cycles_are_unique(self):
        """Ensure funccycles returns no duplicates."""
        for cycles in self.cyclesets:
            self.assertEqual(len(cycles), len(set(cycles)))

    def test_cycles_are_complete(self):
        """Ensure funccycles returns every cycle."""
        for f, lim in zip(self.funcs, self.limitsets):
            self.assertEqual(f.imagepath[-1], len(lim))

    def test_acyclic_ancestors_are_not_cyclic(self):
        """Make sure attached_treenodes returns nodes not in cycles."""
        for f, lim in zip(self.funcs, self.limitsets):
            for _, invim in f.acyclic_ancestors.items():
                for x in invim:
                    self.assertNotIn(x, lim)

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
