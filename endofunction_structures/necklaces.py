#!/usr/bin/env python
# Copyright (C) 2014-2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.

""" A necklace is a class of n-character strings equivalent under rotation
(orbits of the set of n-character strings under the action of cyclic
permutation by the cyclic group). For example, the following are examples of a
necklace using [a,b,c,d], [a,b,b] and [c,d]:

    [a,b,c,d] ~ [b,c,d,a] ~ [c,d,a,b] ~ [d,a,b,c]
    [a,b,b] ~ [b,a,b] ~ [b,b,a]
    [c,d,c,d] ~ [d,c,d,c]

Different necklaces may have different periodicity, as seen above. This module
contains a collection of functions for counting and enumerating necklaces of a
given multiset.

Their relavence to enumerating endofunction structures is as follows: given a
collection of N forests, the necklaces whose beads are the forests' trees are
precisely the distinct ways of connecting the trees to form a cycle of length
n. Thus the ways of connecting a collection of rooted trees together in a cycle
are precisely the necklaces whose beads are the rooted trees. """


import fractions
import functools

from PADS import Lyndon

from . import multiset
from . import factorization


def periodicity(strand):
    """ Find the "periodicity" of a list; i.e. the number of its distinct
    cyclic rotations. Algorithm proposed by Meng Wang (wangmeng@berkeley.edu)
    runs in O(len(strand)). """
    n = len(strand)
    if n in [0, 1]:
        return n
    seed = []
    l = p = 1
    while p != n:
        while not factorization.isdivisor(l, n):
            l += 1
        p = l
        seed.extend(strand[len(seed):p])
        stop = False
        for rep in range(l, n, l):
            for i, val in enumerate(seed):
                l += 1
                if val != strand[rep + i]:
                    stop = True
                    break
            if stop:
                break
        else:
            break
    return len(seed)


class Necklace(object):
    """An equivalence class of all lists equivalent under rotation."""

    def __init__(self, strand):
        """Initialize the necklace. Items in the necklace must be hashable
        (immutable), otherwise the equivalence class could change
        dynamically."""
        self.strand = tuple(Lyndon.SmallestRotation(strand))
        self.period = periodicity(strand)

    def __repr__(self):
        return "Necklace(%s)" % str(self.strand)

    def __len__(self):
        return len(self.strand)

    def __hash__(self):
        return hash(self.strand)

    def __eq__(self, other):
        """For now we check for equality by "brute force" rotation, as D.
        Eppstein's normalization algorithm produces unpredictable output for
        items with ill-defined orderability."""
        if isinstance(other, self.__class__):
            return self.strand == other.strand
        return False

    def __ne__(self, other):
        return not self == other

    def __contains__(self, other):
        try:
            return self == self.__class__(other)
        except:
            return False

    def __iter__(self):
        return iter(self.strand)

    def degeneracy(self):
        return len(self)//self.period


def simple_fixed_content(a, content, t, p, k):
    """ This function is a result of refactoring of Sage's simple fixed content
    algorithm, featured in src/sage/combinat/neckalce.py as of December 23,
    2014. The original code was written by Mike Hansen <mhansen@gmail.com> in
    2007, who based his algorithm on Sawada, Joe. "A fast algorithm to generate
    necklaces with fixed content", Theoretical Computer Science archive Volume
    301 , Issue 1-3, May 2003. """
    n = len(a)
    if t > n and not(n % p):
        yield a
    else:
        for j in range(a[t-p-1], k):
            if content[j] > 0:
                a[t-1] = j
                content[j] -= 1
                tp = p if(j == a[t-p-1]) else t
                for z in simple_fixed_content(a, content, t+1, tp, k):
                    yield z
                content[j] += 1


class NecklaceGroup(object):

    def __init__(self, beads):
        """Form a generator of all necklaces with beads of a given multiset."""
        self.beads = multiset.Multiset(beads)
        self.elems, self.partition = self.beads.split()

    def __repr__(self):
        return self.__class__.__name__+'('+repr(self.beads)+')'

    def __str__(self):
        return 'Necklaces('+str(self.beads)+')'

    def count_by_period(self):
        """ Returns a list whose kth element is the number of necklaces
        corresponding to the input set of beads with k distinct rotations. """
        k = len(self.partition)
        N = sum(self.partition)
        # Each period must be a divisor of the gcd of the multiplicities.
        w = functools.reduce(fractions.gcd, self.partition)
        p0 = N//w
        factors = factorization.divisors(w)
        mults = [0] * (factors[-1] + 1)
        # Find the multiplicity of each period.
        for factor in factors:
            n = period = p0 * factor
            mults[factor] = 1
            # The number of character permutations which are periodic in factor
            # OR ANY OF ITS DIVISORS is simply the multinomial coefficient
            # corresponding to the subset of the multiplicity partition
            # featuring 1/factor of each kind of the original partiton's
            # elements.
            for I in range(k):
                mults[factor] *= multiset.nCk(n, self.partition[I]*factor//w)
                n -= self.partition[I] * factor//w
            # Subtact off the number of character permutations whose period
            # subdivides our divisor of w, to get the number of character
            # permutations with period EXACTLY equal to factor.
            subdivisors = factorization.divisors(factor)
            if subdivisors[-1] != 1:
                for subfactor in subdivisors[:-1]:
                    mults[factor] -= subfactor * p0 * mults[subfactor]
            # Finally, normalize by the period to obtain the number of distinct
            # rotations of any member of mults[factor].
            mults[factor] //= period
        return mults

    def cardinality(self):
        """Return the number of necklaces formed from the given multiset of
        beads."""
        return sum(self.count_by_period())

    def __len__(self):
        return self.cardinality()

    def sfc(self):
        """Wrapper for partition necklaces, which takes a partition of
        multiplicities and enumerates canonical necklaces on that partition."""
        partition = list(self.partition)
        a = [0]*sum(partition)
        partition[0] -= 1
        k = len(partition)
        return simple_fixed_content(a, partition, 2, 1, k)

    def __iter__(self):
        """ Given a set of items (called beads) returns all necklaces which can
        be made with those beads. """
        if not self.beads:
            return
        for strand in self.sfc():
            # Explicitly make a tuple, since we must form the list of all
            # necklaces in memory when constructing endofunction structures.
            yield Necklace([self.elems[I] for I in strand])

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.beads == other.beads
        return False

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(self.beads)
