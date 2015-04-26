"""Let S be a finite set with N elements; i.e. |S|=N. There are N^N
endofunctions defined on this set.

For a given endofunction f, its image will have n=|f(S)| elements for 1 <= n <=
N. Similarly its second iterate will have |f(f(S))|=m<=n elements. Once
|f^(k)(S)|=|f^(k+1)(S)| then |f^(j)(S)|=|f^(k)(S)| for all j>k. The list of
sizes of images of iterates of f from 1 to n-1 is called the "image path" of f.

This module contains methods for calculating the distribution of image sizes of
the iterates of all endofunctions on a set S. The naive way to do this is to
literally enumerate every endofunction. This works for n up to about 8 on a
decent desktop computer.

The second, far more efficient method, is to enumerate the endofunction
structures on S (i.e. orbits of the full transformation monoid under the action
of conjugation by the symmetric group), and then add up the multiplicities of
each structure. This runs in roughly O(4^n) time. This is still quite
horrendous, but it enables us to get up to n=16 before being intolerably slow.

Various special cases can be done much faster. This distribution of (first
iterate) image sizes can be done in O(n^2) and the distribution of last iterate
image sizes set can be O(n) (and has a lovely closed form formula).

Caleb Levy, 2013, 2014 and 2015.
"""

import numpy as np

from . import counts
from . import funcstructs
from . import endofunctions
from . import compositions


def iterdist_brute(n):
    """Calculate iterdist by enumerating all endofunction image paths."""
    dist = np.zeros((n, n-1), dtype=object)
    for f in endofunctions.TransformationMonoid(n):
        for it, card in enumerate(f.imagepath):
            dist[card-1, it] += 1
    return dist


def iterdist_funcstruct(n, cycle_type=None):
    """Every labelling of a function structure shares the same image path, thus
    we may calculate iteration distributions by enumerating all endofunction
    structure image paths and scaling them by their multiplicities.

    TODO: Finalize proof that len(EndofunctionStructures(n)) is O(a^n),
    investigate possibility that a<=4, and add writeup to the repository.
    """
    if n == 1:
        c = 0 if(cycle_type or sum(cycle_type) != 1) else 1
        return np.array([c], dtype=object)
    dist = np.zeros((n, n-1), dtype=object)
    nfac = counts.factorial(n)
    for struct in funcstructs.EndofunctionStructures(n, cycle_type):
        mult = nfac//struct.degeneracy
        for it, card in enumerate(struct.imagepath):
            dist[card-1, it] += mult
    return dist

iterdist = iterdist_funcstruct


def imagedist_composition(n):
    """Produces left column of iterdist using integer compositions in O(2^n)
    operations. The idea of the algorithm comes from a binary tree.

    TODO: place writeup in the notes.
    """
    if n == 1:
        return tuple([1])
    dist = [0]*n
    for comp in compositions.binary_compositions(n):
        val = n
        rep = 1
        for i in comp:
            if not i:
                val *= rep
            else:
                val *= n-rep
                rep += 1
        dist[rep-1] += val
    return tuple(dist)


def imagedists_upto(n):
    """Left column of iterdist. This uses a recursion relation to run in O(n^2)
    time. It is the fastest method I know of and likely the fastest there is.
    The idea behind it is a modified special form of the monomial symmetric
    polynomial algorithm.

    # TODO: place writeup in the nodes.
    """
    dist = np.zeros((n, n), dtype=object)
    for i in range(n):
        dist[0, i] = dist[i, i] = 1
        for j in range(i):
            dist[j, i] = dist[j-1, i-1] + (j+1)*dist[j, i-1]
    for i in range(n):
        for j in range(i+1):
            dist[j, i] *= counts.factorial(i+1)//counts.factorial(i-j)
    return dist

imagedist_recurse = imagedist = lambda n: list(imagedists_upto(n)[:, -1])


def nCk_grid(n):
    """nCk(i, j) == nCk_table[i, j] for 0 <= j <= i <= m. """
    binomial_coeffs = np.zeros((n+1, n+1), dtype=object)
    for i in range(n+1):
        for j in range(n+1):
            if j > i:
                continue
            binomial_coeffs[i, j] = counts.nCk(i, j)
    return binomial_coeffs


def powergrid(n):
    """i**j == powergrid[i, j] for 0 <= i, j <= n. Note 0**0 defined as 1."""
    base = np.arange(n+1, dtype=object)
    bases, exponents = np.meshgrid(base, base)
    exponentials = bases**exponents
    return exponentials.T


def limitdist_composition(n):
    """Right column of iterdist. Idea of the algorithm is the calculate the
    number of functions corresponding to each level path (distribution of nodes
    by height), which happens to correspond with compositions of a number.

    The number of endofunctions with a given level path L=[l0, l1, ..., ln] is
    given by the number of functions from a set with ln to ln-1 elements, times
    the number of labellings, multiplied by the number of endofunctions from
    ln-1 to ln-2 times the number of possible remaining labellings, and so
    forth.

    The idea works for the last iterate because we may by definition assume
    everything ends up in l0. I tried for many months to expand on this idea
    for the general case, and failed, since there may be many image paths
    corresponding to a given level path; conversely one image path may be found
    from functions of many different image paths. """
    dist = [0]*n
    # Memoize these lookups; saves a lot of time.
    exponentials = powergrid(n)
    binomial_coefficients = nCk_grid(n)
    for comp in compositions.compositions(n):
        count = 1
        for i in range(1, len(comp)):
            count *= exponentials[comp[i-1], comp[i]]
            count *= binomial_coefficients[sum(comp[i:]), comp[i]]
        dist[comp[0]-1] += count
    for i in range(n, 0, -1):
        dist[i-1] *= counts.factorial(n)//counts.factorial(n-i)
    return tuple(dist)


def limitset_count(n, k):
    """Analytic expression for the number of endofunctions on n nodes whose
    cycle decompositions contain k elements. """
    return k*n**(n-k)*counts.factorial(n-1)//counts.factorial(n-k)


def limitdist_direct(n):
    """Exact formula for the right-hand column of iterdist(n)"""
    return tuple(limitset_count(n, k) for k in range(1, n+1))


def limitdist_recurse(n):
    """Faster way to find the limitdist which reduces duplication of work. I
    discovered the above two formulas from this recursion relation, which I
    derived empirically from the output of limitdist_composition.

    TODO: derive and writeup the equivalence of these algorithms.
    """
    dist = [n**(n-1)]+[0]*(n-1)
    for k in range(1, n):
        dist[k] = (dist[k-1]*(k+1)*(n-k))//(k*n)
    return tuple(dist)

limitdist = limitdist_recurse
