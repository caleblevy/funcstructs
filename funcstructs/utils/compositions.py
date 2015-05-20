"""A composition of an integer N is an ordered tuple of positive integers
which sum to N, for example:

    4 = 4
      = 3 + 1
      = 2 + 2
      = 2 + 1 + 1
      = 1 + 3
      = 1 + 2 + 1
      = 1 + 1 + 2
      = 1 + 1 + 1 +1

The compositions of 4 are thus (4), (3,1), (2,2), (2,1,1), (1,3), (1,2,1),
(1,1,2) and (1,1,1,1).

One can see a clear correspondence between compositions of N and the subsets of
a set with N-1 elements. Simply list N zeros in a row; every way to draw
dividing lines between the zeros is a different composition. These correspond
to binary digits of numbers of length up to N-1. There are thus 2^(N-1)
compositions of N.

Caleb Levy, 2014 and 2015.
"""

from funcstructs.structures import productrange


def binary_compositions(n):
    """The division marker representation of each composition."""
    return productrange.productrange([2]*(n-1))


def compositions(n):
    """Enumerate ordered lists of positive integers summing to n."""
    comp = [n]
    while comp:
        yield comp
        j = len(comp)
        for k in range(j-1, -1, -1):
            # Keep descending (backwards) until hitting a component you can
            # subtract from
            if comp[k] > 1:
                comp[k] -= 1
                comp.append(j-k)
                break
            # Haven't hit a 1, pop the last element, and step back
            comp.pop()


def weak_compositions(n, k):
    """Enumerates the length k lists of non-negative integers summing to n.
    Taken directly from http://dandrake.livejournal.com/83095.html."""
    if n < 0 or k < 0:
        return
    elif k == 0:
        # the empty sum, by convention, is zero, so only return something if
        # n is zero
        if n == 0:
            yield []
        return
    elif k == 1:
        yield [n]
        return
    else:
        # For each first integer i in range(n+1), list all compositions
        # on n-i nodes, of length at most k-1.
        for i in range(n+1):
            for comp in weak_compositions(n-i, k-1):
                yield [i] + comp
