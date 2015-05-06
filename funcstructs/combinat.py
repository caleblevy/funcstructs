"""Collection of functions for basic combinatorial counting.

Caleb Levy, 2015.
"""

import itertools
from math import factorial

from .multiset import (
    Multiset,
    _prod as prod,
    _factorial_prod as factorial_prod
)


def nCk(n, k):
    """n choose k == n!/k!/(n-k)!, optimized for large n and small k"""
    return factorial(n)//factorial(k)//factorial(n-k)


def multinomial_coefficient(partition, n=None):
    """The multinomial coefficient of n corresponding to partition [p1, ...,
    pk] is given by n!/(p1! *...* pk!)/(n-sum(partition))!"""
    p = sum(partition)
    if n is None:
        n = p
    return factorial(n)//factorial_prod(partition)//factorial(n-p)


def nCWRk(n, r):
    """Returns nCk(n+r-1, n-1) optimized for large n and small r."""
    val = 1
    for i in range(1, r+1):
        val *= n + r - i
        val //= i
    return val


def unordered_product(mset, iterfunc):
    """Given a multiset of inputs to an iterable, and iterfunc, returns all
    unordered combinations of elements from iterfunc applied to each el. It is
    equivalent to:

        set(Multiset(p) for p in product([iterfunc(i) for i in mset]))

    except it runs through each element once. This program makes the
    assumptions that no two members of iterfunc(el) are the same, and that if
    el1 != el2 then iterfunc(el1) and iterfunc(el2) are mutually disjoint."""
    mset = Multiset(mset)
    strands = []
    for y, d in mset.items():
        strands.append(itertools.combinations_with_replacement(iterfunc(y), d))
    for bundle in itertools.product(*strands):
        yield Multiset(itertools.chain.from_iterable(bundle))
