"""Functions for iterating over dynamically nested loops.

Caleb Levy, 2014 and 2015.
"""

import itertools

from . import multiset

__all__ = ["productrange", "rev_range", "unordered_product"]


def _parse_ranges(begin, end, step):
    """If begin == end == None then begin is treated as end and step is set by
    default to 1 and begin to 0. If begin and step are integers they are
    transformed into begin = [begin]*len(end) and step = [step]*len(end)."""
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


def _product_sets(b, e, s):
    """List of ranges over which the product will be taken"""
    return [range(i, j, k) for i, j, k in zip(*_parse_ranges(b, e, s))]


def productrange(begin, end=None, step=None):
    """Nice wrapper for itertools.product. Accepts a tuple of starts, stops and
    increments and it will return the nested for loop corresponding to them.
    If:
        begin = (r1, r2, ..., rm)
        end = (s1, s2, ..., sm)
        step = (t1, t2, ..., tm)
    then:
        productrange(begin, end, step) <==> [(i1, i2, ..., im)
                                             for i1 in range(r1, s1, t1)
                                               for i2 in range(r2, s2, t2)
                                                 ...
                                                   for im in range(rm, sm, tm)]
    """
    return itertools.product(*_product_sets(begin, end, step))


def rev_range(begin, end=None, step=None):
    """Reverse iteration order for productrange, i.e.
        rev_range(begin, end, step) <==> [(i1, i2, ..., im)
                                          for in in range(rm, sm, tm)
                                            ...
                                              for i2 in range(r2, s2, t2)
                                                for i1 in range(r1, s1, t1)]
    Code originally inspired by:
        http://www.mathworks.com/matlabcentral/answers/79986#answer_89700."""
    b, e, s = _parse_ranges(begin, end, step)
    if not all(map(len, _product_sets(b, e, s))):
        return
    e = list(map(abs, e))
    vec = list(b)
    go = True
    while go:
        yield vec
        vec[0] += s[0]
        if abs(vec[0]) >= e[0]:
            vec[0] = b[0]
            go = False
            for i in range(1, len(e)):
                vec[i] += s[i]
                if abs(vec[i]) < e[i]:
                    go = True
                    break
                vec[i] = b[i]


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
        yield multiset.Multiset(itertools.chain.from_iterable(bundle))
