#!/usr/bin/env python
# Copyright (C) 2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.

from operator import gt, ge, le, lt
import itertools


def monotone_subsequences(seq, comparison):
    """ Given an iterable seq and a comparsion function, returns a generator of
    the subsequences of seq such that comparison(seq[I],seq[I+1]) holds for
    0<=I<=len(seq)-1.

    For example, if comparison is >=, then this returns nondecreasing
    subsequences, while comparison of > returns increasing. Equivalent to
    sympy's runs() method. """
    if not seq:
        return
    subseq = []
    for term in seq:
        if not subseq:
            subseq = [term]
        else:
            if comparison(term, term_prev):
                subseq.append(term)
            else:
                yield subseq
                subseq = [term]
        term_prev = term
    yield subseq

increasing_subsequences = lambda seq: monotone_subsequences(seq, gt)
nondecreasing_subsequences = lambda seq: monotone_subsequences(seq, ge)
decreasing_subsequences = lambda seq: monotone_subsequences(seq, lt)
nonincreasing_subsequences = lambda seq: monotone_subsequences(seq, le)


def startswith(seq, cond):
    """ Given a sequence seq and boolean function of a single input cond,
    returns a generator of subsequences such that a new subsequence begins if
    and only if cond is true for the first element in the subsequence. If cond
    is never true, returns the original sequence. """
    if not seq:
        return
    subseq = []
    for el in seq:
        if cond(el) and subseq:
            yield subseq
            subseq = [el]
        else:
            subseq.append(el)
    yield subseq


def endswith(seq, cond):
    """ Return a generator returning subsequences of seq each ending with an
    element satisfying the boolean lambda function cond. """
    if not seq:
        return
    subseq = []
    for el in seq:
        subseq.append(el)
        if cond(el):
            yield subseq
            subseq = []
    if not cond(el):
        yield subseq
