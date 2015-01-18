#!/usr/bin/env python
# Copyright (C) 2014-2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.


"""
Functions for iterating over dynamically nested loops; i.e. iterating over
cartesian products of finite sets, with variable dimensionality.
"""


import unittest
from itertools import product
from multiset import prod


isiterable = lambda obj: hasattr(obj, '__iter__')


def parse_ranges(begin, end, step):
    """
    If begin == end == None then begin is treated as end and step is set by
    default to 1 and begin to 0. If begin and step are integers they are
    transformed into begin = [begin]*len(end) and step = [step]*len(end).
    """
    if end is None:
        begin, end = end, begin
    # If start is not iterable, it is either an int or none.
    if not isiterable(begin):
        begin = [0 if(begin is None) else begin]*len(end)

    if not isiterable(step):
        step = [1 if(step is None) else step]*len(end)

    if not len(begin) == len(step) == len(end):
        raise ValueError("begin, end, and step do not match in length.")

    return begin, end, step


def product_range(begin, end=None, step=None):
    """
    Nice wrapper for itertools.product. Give it a tuple of starts, stops and
    increments and it will return the nested for loop coresponding to them.
    I.E. if begin = (r1, r2, ..., rn), end = (s1, s2, ..., sn) and step =
    (t1, t2, ..., tn) then

        for tup in product_range(begin, end, step):
            yield tup

    is equivalent to:

        for I1 in range(r1, s1, t1):
          for I2 in range(r2, s2, t2):
            ...
              for I in range(rn, sn, tn):
                yield tuple([I1, I2, ..., In])
    """
    begin, end, step = parse_ranges(begin, end, step)
    return product(*[range(I, J, K) for I, J, K in zip(begin, end, step)])

endofunctions = lambda n: product_range([n]*n)


class ProductrangeTest(unittest.TestCase):

    def testProductRange(self):
        begins = [None,   0,      1,      [1]*4,   [3]*4,  (1, 2, 3, 3)]
        ends = [[4]*4,    [4]*4,  [7]*3,  [10]*4,  [6]*4,  (2, 4, 8, 10)]
        steps = [1,       None,   2,       3,      None,   (1, 1, 2, 2)]

        counts = [4**4,   4**4,   3**3,   3**4,    3**4,   1*2*3*4]
        for c, b, e, s in zip(counts, begins, ends, steps):
            self.assertEqual(c, len(list(product_range(b, e, s))))
            self.assertEqual(prod(e), len(list(product_range(e))))


if __name__ == '__main__':
    unittest.main()
