"""Algorithms for representing and enumerating necklaces: ordered lists
equivalent under cyclic rotation.

Caleb Levy, 2014 and 2015.
"""

from collections import Sequence
from fractions import gcd
from functools import reduce

from PADS.Lyndon import SmallestRotation

from funcstructs import bases
from funcstructs.utils.combinat import multinomial_coefficient
from funcstructs.utils.factorization import divisors

from .multiset import Multiset


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


class Necklace(bases.Tuple):
    """A necklace is the lexicographically smallest representative of a class
    of n-character strings equivalent under rotation (orbits of the set of
    n-character strings under the action of the cyclic group). For example the
    following are necklaces, and the classes they represent:

        Necklace([a,b,c,d]) :==: {(a,b,c,d), (b,c,d,a), (c,d,a,b), (d,a,b,c)}
        Necklace([c,d,c,d]) :==: {(c,d,c,d), (d,c,d,c)}
        Necklace([1,2,2])   :==: {(1,2,2), (2,1,2), (2,2,1)}

    Different necklaces may have different periodicity, as seen above.
    """

    __slots__ = ()

    def __new__(cls, word):
        """Initialize the necklace. Items in the necklace must be hashable
        (immutable), otherwise the equivalence class could change
        dynamically.

        Inputs must also be comparable or you may get unpredictable results.
        Input content is normalized to smallest rotation unless preordered is
        set to true. Only use this option if you can (mathematically) prove
        that your input is in lexicographically smallest form."""
        # Explicitly check for tuple and list first for speed, since ABC
        # instancechecks are expensive.
        if not isinstance(word, (tuple, list, Sequence)):
            word = tuple(word)
        self = super(Necklace, cls).__new__(cls, SmallestRotation(word))
        try:
            hash(self)
        except TypeError:
            raise TypeError("Necklace content must be hashable and immutable")
        return self

    def degeneracy(self):
        """Number of distinct representations of the same necklace."""
        return len(self)//periodicity(self)


def _sfc(multiplicities):
    """Wrapper for partition necklaces, which takes a partition of
    multiplicities and enumerates canonical necklaces on that partition."""
    content = list(multiplicities)
    a = [0]*sum(content)
    content[0] -= 1
    k = len(content)
    return _simple_fixed_content(a, content, 2, 1, k)


def _simple_fixed_content(a, content, t, p, k):
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
                for z in _simple_fixed_content(a, content, t+1, tp, k):
                    yield z
                content[j] += 1


class FixedContentNecklaces(bases.Enumerable):
    """Enumerator of necklces with a fixed content."""

    def __init__(self, content=None, multiplicities=None):
        if multiplicities is None:
            content, multiplicities = zip(*sorted(Multiset(content).items()))
        elif content is None:
            # already sorted by construction if just multiplicites
            content, multiplicities = zip(*enumerate(multiplicities))
            if not all(isinstance(v, int) and v > 0 for v in multiplicities):
                raise TypeError("Multiplicities must be positive integers")
        else:
            # Must make them into sequences for length checking
            content = tuple(content)
            multiplicities = tuple(multiplicities)
            if len(content) != len(multiplicities):
                raise TypeError("content and and multiplicities do not match")
            # TODO: Add Multiset.from_items
            m = Multiset.fromitems(zip(content, multiplicities))
            content, multiplicities = zip(*sorted(m.items()))
        try:
            hash(content)
        except TypeError:
            raise TypeError("Necklace content must be hashable and immutable")
        self.content = content
        self.multiplicities = multiplicities

    def count_by_period(self):
        """Returns a list whose kth element is the number of necklaces
        corresponding to the input set of beads with k distinct rotations.
        """
        n = sum(self.multiplicities)
        # Each period must be a divisor of the gcd of the multiplicities.
        w = reduce(gcd, self.multiplicities)
        baseperiod = n//w
        factors = divisors(w)
        mults = [0] * (factors[-1] + 1)
        # Find the multiplicity of each period.
        for factor in factors:
            period = baseperiod * factor
            # The number of character permutations which are periodic in any
            # divisor of factor is simply the multinomial coefficient
            # corresponding to the subset of the multiplicity partition
            # featuring 1/factor of each kind of the original partiton's
            # elements.
            mults[factor] = multinomial_coefficient(
                [(i*factor)//w for i in self.multiplicities]
            )
            # To enusre mults[factor] gives the number of character
            # permutations with period exactly equal to (not subdividing)
            # factor, subtact off the number of permutations whose period
            # subdivides our factor.
            subdivisors = divisors(factor)
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

    def __iter__(self):
        elem_get = self.content.__getitem__
        for strand in _sfc(self.multiplicities):
            # Explicitly make a tuple, since we must form the list of all
            # necklaces in memory when constructing endofunction structures.
            yield tuple.__new__(Necklace, map(elem_get, strand))

    @bases.typecheck(Necklace)
    def __contains__(self, other):
        m = Multiset(other)
        for k, v in zip(self.content, self.multiplicities):
            if m[k] != v:
                break
        else:
            return True
        return False
