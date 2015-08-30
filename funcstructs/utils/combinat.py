"""Collection of functions for basic combinatorial counting.

Caleb Levy, 2015.
"""

from functools import reduce
from math import factorial
from operator import mul

from funcstructs.structures.multiset import (
    _prod as prod,
    _factorial_prod as factorial_prod
)


def nCk(n, k):
    """n choose k == n!/k!/(n-k)!, optimized for large n and small k"""
    return factorial(n)//factorial(k)//factorial(n-k)


def multinomial_coefficient(partition, n=None):
    """The multinomial coefficient of n corresponding to partition [p1, ...,
    pk] is given by n!/(p1! *...* pk!)/(n-sum(partition))!"""
    tot = 0
    deg = 1
    for p in partition:
        tot += p
        deg *= factorial(p)
    if n is None:
        n = tot
    return factorial(n)//deg//factorial(n-tot)


def nCWRk(n, r):
    """Returns nCk(n+r-1, n-1) optimized for large n and small r."""
    val = 1
    for i in range(1, r+1):
        val *= n + r - i
        val //= i
    return val
