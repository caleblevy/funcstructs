"""Algorithms for representing and enumerating necklaces: ordered lists
equivalent under cyclic rotation.

Caleb Levy, 2014 and 2015.
"""

import fractions
import functools

from memoized_property import memoized_property
from PADS import Lyndon

from . import factorization
from . import counts
from . import enumerable


def periodicity(strand):
    """ Find the "periodicity" of a list; i.e. the number of its distinct
    cyclic rotations. Algorithm proposed by Meng Wang (wangmeng@berkeley.edu)
    runs in O(len(strand)). """
    n = len(strand)
    if n in {0, 1}:
        return n
    seed = []
    l = p = 1
    while p != n:
        while n % l:
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


class Necklace(tuple):
    """A necklace is the lexicographically smallest representative of a class
    of n-character strings equivalent under rotation (orbits of the set of
    n-character strings under the action of the cyclic group). For example the
    following are necklaces, and the classes they represent:

        Necklace([a,b,c,d]) :==: {(a,b,c,d), (b,c,d,a), (c,d,a,b), (d,a,b,c)}
        Necklace([c,d,c,d]) :==: {(c,d,c,d), (d,c,d,c)}
        Necklace([1,2,2])   :==: {(1,2,2), (2,1,2), (2,2,1)}

    Different necklaces may have different periodicity, as seen above.
    """

    def __new__(cls, strand, preordered=False):
        """Initialize the necklace. Items in the necklace must be hashable
        (immutable), otherwise the equivalence class could change
        dynamically.

        Inputs must also be comparable or you may get unpredictable results.
        Input content is normalized to smallest rotation unless preordered is
        set to true. Only use this option if you can (mathematically) prove
        that your input is in lexicographically smallest form."""
        if not preordered:
            strand = Lyndon.SmallestRotation(strand)
        return super(Necklace, cls).__new__(cls, strand)

    @memoized_property
    def period(self):
        return periodicity(self)

    def __repr__(self):
        return self.__class__.__name__+"(%s)" % list(self)

    def degeneracy(self):
        """Number of distinct representations of the same necklace."""
        return len(self)//self.period


def simple_fixed_content(a, content, t, p, k):
    # This function is a result of refactoring of Sage's simple fixed content
    # algorithm, featured in src/sage/combinat/neckalce.py as of December 23,
    # 2014. The original code was written by Mike Hansen <mhansen@gmail.com> in
    # 2007, who based his algorithm on Sawada, Joe. "A fast algorithm to
    # generate necklaces with fixed content", Theoretical Computer Science
    # archive Volume 301 , Issue 1-3, May 2003, which may be found in the
    # references.
    n = len(a)
    if t > n and not n % p:
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


class FixedContentNecklaces(enumerable.Enumerable):
    """ Representation of the set of necklaces of fixed content; i.e. a fixed
    pool of beads from which to form necklaces. """

    def __init__(self, content):
        """Form a generator of all necklaces with beads of a given multiset."""
        super(FixedContentNecklaces, self).__init__(None, content)
        self.elements, self.multiplicities = self.partition.sort_split()

    @classmethod
    def from_partition(cls, partition):
        beads = []
        for i, d in enumerate(partition):
            beads.extend([i+1]*d)
        return cls(beads)

    def count_by_period(self):
        """Returns a list whose kth element is the number of necklaces
        corresponding to the input set of beads with k distinct rotations.
        """
        n = sum(self.multiplicities)
        # Each period must be a divisor of the gcd of the multiplicities.
        w = functools.reduce(fractions.gcd, self.multiplicities)
        baseperiod = n//w
        factors = factorization.divisors(w)
        mults = [0] * (factors[-1] + 1)
        # Find the multiplicity of each period.
        for factor in factors:
            period = baseperiod * factor
            # The number of character permutations which are periodic in any
            # divisor of factor is simply the multinomial coefficient
            # corresponding to the subset of the multiplicity partition
            # featuring 1/factor of each kind of the original partiton's
            # elements.
            mults[factor] = counts.multinomial_coefficient(
                [(i*factor)//w for i in self.multiplicities]
            )
            # To enusre mults[factor] gives the number of character
            # permutations with period exactly equal to (not subdividing)
            # factor, subtact off the number of permutations whose period
            # subdivides our factor.
            subdivisors = factorization.divisors(factor)
            if subdivisors[-1] != 1:
                for subfactor in subdivisors[:-1]:
                    mults[factor] -= subfactor * baseperiod * mults[subfactor]
            # Finally, normalize by the period: the number of distinct
            # rotations of any member of mults[factor], to obtain the number of
            # distinct necklaces with this period.
            mults[factor] //= period
        return mults

    def cardinality(self):
        return sum(self.count_by_period())

    def sfc(self):
        """Wrapper for partition necklaces, which takes a partition of
        multiplicities and enumerates canonical necklaces on that partition."""
        multiplicities = list(self.multiplicities)
        a = [0]*sum(multiplicities)
        multiplicities[0] -= 1
        k = len(multiplicities)
        return simple_fixed_content(a, multiplicities, 2, 1, k)

    def __iter__(self):
        if not self.partition:
            return
        for strand in self.sfc():
            # Explicitly make a tuple, since we must form the list of all
            # necklaces in memory when constructing endofunction structures.
            yield Necklace([self.elements[i] for i in strand], preordered=True)
