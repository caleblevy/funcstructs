"""Caleb Levy, 2015."""

import operator
import functools


def runs(seq, comparison):
    """ Given an iterable seq and a comparison function, returns a generator of
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


def runner(comparison):
    """Generator function factory for monotone subsequences."""
    return functools.partial(runs, comparison=comparison)

increasing = runner(operator.gt)
nondecreasing = runner(operator.ge)
decreasing = runner(operator.lt)
nonincreasing = runner(operator.le)


def startswith(seq, start):
    """ Given a sequence seq and boolean function of a single input cond,
    returns a generator of subsequences such that a new subsequence begins if
    and only if cond is true for the first element in the subsequence. If cond
    is never true, returns the original sequence. """
    if not seq:
        return
    subseq = []
    for el in seq:
        if el == start and subseq:
            yield subseq
            subseq = [el]
        else:
            subseq.append(el)
    yield subseq


def endswith(seq, end):
    """ Return a generator returning subsequences of seq each ending with an
    element satisfying the boolean lambda function cond. """
    if not seq:
        return
    subseq = []
    for el in seq:
        subseq.append(el)
        if el == end:
            yield subseq
            subseq = []
    if el != end:
        yield subseq
