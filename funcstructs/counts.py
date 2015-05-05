"""Collection of functions for basic combinatorial counting.

Caleb Levy, 2015.
"""

import functools
import operator
from math import factorial


def prod(iterable):
    """Product of all items in an iterable."""
    return functools.reduce(operator.mul, iterable, 1)


def factorial_prod(iterable):
    """Product of factorial of elements in an iterable."""
    return prod(factorial(i) for i in iterable)


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
