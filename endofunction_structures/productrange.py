# Copyright (C) 2014-2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.


""" Functions for iterating over dynamically nested loops. """

import itertools

from . import multiset


def flatten(lol):
    """Flatten a list of lists."""
    return list(itertools.chain.from_iterable(lol))


def parse_ranges(begin, end, step):
    """ If begin == end == None then begin is treated as end and step is set by
    default to 1 and begin to 0. If begin and step are integers they are
    transformed into begin = [begin]*len(end) and step = [step]*len(end). """
    if end is None:
        begin, end = end, begin
    # If start is not iterable, it is either an int or none.
    if not hasattr(begin, '__iter__'):
        begin = [0 if(begin is None) else begin]*len(end)
    if not hasattr(step, '__iter__'):
        step = [1 if(step is None) else step]*len(end)
    if not len(begin) == len(step) == len(end):
        raise ValueError("begin, end, and step do not match in length.")
    return begin, end, step


def productrange(begin, end=None, step=None):
    """ Nice wrapper for itertools.product. Give it a tuple of starts, stops
    and increments and it will return the nested for loop coresponding to them.
    I.E. if begin = (r1, r2, ..., rn), end = (s1, s2, ..., sn) and step = (t1,
    t2, ..., tn) then

        for tup in productrange(begin, end, step):
            yield tup

    is equivalent to:

        for I1 in range(r1, s1, t1):
          for I2 in range(r2, s2, t2):
            ...
              for In in range(rn, sn, tn):
                yield tuple([I1, I2, ..., In])
    """
    b, e, s = parse_ranges(begin, end, step)
    return itertools.product(*[range(i, j, k) for i, j, k in zip(b, e, s)])


def rev_range(begin, end=None, step=None):
    """ Reverse iteration order for productrange. If begin, end and step are
    as for productrange, then

        for tup in rev_range(begin, end, step):
            yield tup

    is equivalent to:

        for In in range(rn, sn, tn):
          ...
            for I2 in range(r2, s2, t2):
              for I1 in range(r1, s1, t1):
                yield tuple([I1, I2, ..., In])

    Note that set(rev_range(**inputs)) == set(productrange(**inputs)). Code
    originally inspired by:
        http://www.mathworks.com/matlabcentral/answers/79986#answer_89700. """

    begin, end, step = parse_ranges(begin, end, step)
    if not all([len(range(I, J, K)) for I, J, K in zip(begin, end, step)]):
        return
    end = [abs(I) for I in end]
    l = len(end)
    V = list(begin)
    go = True
    while go:
        yield V
        V[0] += step[0]
        # If (>=) <=> (if not <)
        if abs(V[0]) >= end[0]:
            V[0] = begin[0]
            go = False
            for I in range(1, l):
                V[I] += step[I]
                if abs(V[I]) < end[I]:
                    go = True
                    break
                V[I] = begin[I]


def unordered_product(mset, iterfunc):
    """Given a multiset of inputs to an iterable, and iterfunc, returns all
    unordered combinations of elements from iterfunc applied to each el. It is
    equivalent to:

        set(Multiset(p) for p in product([iterfunc(i) for i in mset]))

    except it runs through each element once. This program makes the
    assumptions that no two members of iterfunc(el) are the same, and that if
    el1 != el2 then iterfunc(el1) and iterfunc(el2) are mutually disjoint."""
    mset = multiset.Multiset(mset)
    strands = []
    for y, d in mset.items():
        strands.append(itertools.combinations_with_replacement(iterfunc(y), d))
    for bundle in itertools.product(*strands):
        yield multiset.Multiset(flatten(bundle))
