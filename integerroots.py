#!/usr/bin/env python
# Copyright (C) 2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas \
# contained herein are described in the LICENSE file included with this ]
# project. For more information please contact me at caleb.levy@berkeley.edu.

"""integerroots.py
This module contains a collection of functions collected from stackoverflow.com
for calculating integer roots of a number; i.e. r=iroot(n,k) is the greatest
integer such that r**k<=n. """


import unittest


def iroot_newton(n, k=2):
    """ Given input integer n, return the greatest integer whose kth power is
    less than or equal to n. This algorithm works by Newton's method. Code
    taken directly from "How to find integer nth roots?" at
    http://stackoverflow.com/a/15979957. """

    if not n:
        return 0
    u, s = n, n+1
    while u < s:
        s = u
        t = (k-1) * s + n // pow(s, k-1)
        u = t // k
    return s


def iroot(n, k=2):
    """ Given input integer n, return the greatest integer whose kth power is
    less than or equal to n. This algorithm works by binary search. Code taken
    directly from "How to find integer nth roots?" at
    http://stackoverflow.com/a/15979957. """

    hi = 1
    while pow(hi, k) < n:
        hi *= 2
    lo = hi // 2
    while hi - lo > 1:
        mid = (lo + hi) // 2
        midToK = pow(mid, k)
        if midToK < n:
            lo = mid
        elif n < midToK:
            hi = mid
        else:
            return mid

    if pow(hi, k) == n:
        return hi
    else:
        return lo


def isqrt(n):
    """ Faster method of iroot for the particular case of the integer square
    root. Code taken directly from "Integer square root in python" at
    http://stackoverflow.com/a/15391420. """

    x = n
    y = (x + 1) // 2
    while y < x:
        x = y
        y = (x + n // x) // 2
    return x


class RootTest(unittest.TestCase):
    roots = list(range(1000))+[2**96]+[2**87+2**41]

    def testIntegerRoots(self):
        for val in self.roots:
            for power in range(1, 5):
                self.assertTrue(iroot(val, power)**power <= val)
                self.assertTrue(val < (iroot(val, power)+1)**power)

                self.assertTrue(iroot_newton(val, power)**power <= val)
                self.assertTrue(val < (iroot_newton(val, power)+1)**power)

    def testISqrt(self):
        for val in self.roots:
            self.assertTrue(isqrt(val)**2 <= val)
            self.assertTrue(val < (isqrt(val)+1)**2)


if __name__ == '__main__':
    unittest.main()
