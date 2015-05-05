"""Further functions for enumerating and counting partitions.

Caleb Levy, 2014 and 2015.
"""

import collections
import itertools

from PADS import IntegerPartitions

from . import multiset


def isqrt(n):
    """Returns the integer square root of n; i.e. r=isqrt(n) is the greatest
    integer such that r**2<=n. Code taken directly from "Integer square root in
    python" at http://stackoverflow.com/a/15391420."""
    x = n
    y = (x + 1) // 2
    while y < x:
        x = y
        y = (x + n // x) // 2
    return x


# Wrappers for Eppstein's modules returning multisets
def partitions(n):
    """Wrapper for D Eppstein's partitions return multisets"""
    for partition in IntegerPartitions.partitions(n):
        yield multiset.Multiset(partition)


def fixed_length_partitions(n, w):
    """Wrapper for D Eppstein's fixed_length_partitions returning multisets."""
    for partition in IntegerPartitions.fixed_length_partitions(n, w):
        yield multiset.Multiset(partition)


def tuple_partitions(n):
    """Generates dictionaries with integer keys such that sum(i*d[i] for i in
    d.keys()) == n."""
    mults = collections.defaultdict(int)
    for part in IntegerPartitions.partitions(n):
        for p in part:
            mults[p] += 1
        yield mults
        mults.clear()


def _min_part(n, w):
    """Helper function for fixed_lex_partitions. Returns a tuple containing:
        1) The output of minimal_partition(n,L)
        2) #(Occurances of 1 in this partition)+1.

    The second output is returned so as to avoid calling the count() method of
    the list corresponding to the partition, since this information is
    necessarily contained in the process of its creation. It is needed by
    fixed_lexed_partitions for the index on which to decrement."""
    binsize = n//w
    overstuffed = n - w*binsize
    regular = w - overstuffed
    ones_count = 0 if binsize != 1 else regular
    return [binsize+1]*overstuffed + [binsize]*regular, ones_count


def minimal_partition(n, w):
    """A wrapper for _min_partition. Given integers n > 0 and w <= n, returns
    the lexicographically smallest unordered integer partition of n into L
    nonzero parts."""
    min_part, _ = _min_part(n, w)
    return min_part


def fixed_lex_partitions(n, w):
    """Integer partitions of n into w parts, in lexicographic order. This
    algorithm was derived and implemented by Caleb C. Levy in 2014. Its form
    was taken from David Eppstein's equivalent generator for fixed length
    partitions in colex order."""
    if w == 0:
        if n == 0:
            yield []
        return
    if w == 1:
        if n > 0:
            yield [n]
        return
    if n < w:
        return

    partition, j = _min_part(n, w)
    while True:
        # Algorithm starts with minimal partition, and index of the last 1
        # counting backwards. We then decrement the rightmost components and
        # increment those to their immediate left, up to the point where the
        # partition would beak ordering.
        #
        # Once we have decremented as far as possible, we append the new
        # minimum partition, and repeat.
        yield partition
        k = 2
        s = j + partition[w-j-1] - 1
        while j+k < w and partition[w-j-k-1] == partition[w-j-2]:
            s += partition[w-j-2]
            k += 1
        if j+k > w:
            return
        k -= 1
        partition[w-j-k-1] += 1
        partition[w-j-k:], j = _min_part(s, j+k)


def partition_numbers_upto(n):
    """ Uses Euler's Pentagonal Number Theorem to count partition number using
    the previous terms. The sum is taken over O(sqrt(n)) terms on each pass, so
    the algorithm runs in O(n**3/2). See the Knoch paper in papers folder for a
    proof of the theorem. """
    if n == 0:
        return [1]
    pcounts = [1]+[0]*n
    for m in range(1, n+1):
        k_max = (isqrt(24*m+1)-1)//6
        k_min = -((isqrt(24*m+1)+1)//6)
        for k in itertools.chain(range(k_min, 0), range(1, k_max+1)):
            pcounts[m] += (-1)**abs(k-1) * pcounts[m-k*(3*k+1)//2]
    return pcounts


def partition_number(n):
    return partition_numbers_upto(n)[-1]


def max_length_partitions(n, k):
    """Enumerate partitions of length less than or equal to k."""
    if k >= n:
        for part in partitions(n):
            yield part
    else:
        for l in range(1, k+1):
            for part in fixed_length_partitions(n, l):
                yield part
