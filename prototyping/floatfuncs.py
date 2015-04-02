# Copyright (C) 2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.

"""Module for computing conjugacy classes of self mappings on floating point
numbers."""

import numpy as np

from endofunction_structures import *

Inf = np.float16('inf')
NaN = np.float16('nan')
Max16 = np.float16(65504.0)
Min16 = -Max16
Zero = np.float16(0)
One = np.float16(1)


def short_floats():
    yield -Inf
    f = Min16
    yield f
    while f < Max16:
        f = np.nextafter(f, Inf, dtype=np.float16)
        yield f
    yield Inf
    yield NaN


def positive_floats():
    f = Zero
    yield f
    while f < Max16:
        f = np.nextafter(f, Inf, dtype=np.float16)
        yield f
    yield Inf


INTS_TO_FLOATS = list(short_floats())
INTS_TO_PFLOATS = list(positive_floats())

FLOATS_TO_INTS = {}
PFLOATS_TO_INTS = {}

for i, f in enumerate(INTS_TO_FLOATS):
    FLOATS_TO_INTS[f] = i

for i, f in enumerate(INTS_TO_PFLOATS):
    PFLOATS_TO_INTS[f] = i


def pinteger_form(f):
    """Return a conjugate of f mapped from ints to ints"""
    fi = [0]*len(f)
    for x, y in f.items():
        fi[PFLOATS_TO_INTS[x]] = PFLOATS_TO_INTS[y]
    return fi


def integer_form(f):
    fi = [0]*(len(f)+2)
    for x, y in f.items():
        fi[FLOATS_TO_INTS[x]] = FLOATS_TO_INTS[y]
    return fi


if __name__ == '__main__':
    square = {}
    for f in positive_floats():
        square[f] = f*f
    square_func = Endofunction(pinteger_form(square))
    square_struct = Funcstruct(square_func)
    print square_func
    print square_struct

    x_prev = 0
    x = One
    i = 1
    while x != x_prev:
        print i, repr(x)
        i += 1
        x_prev = x
        x = np.sin(x)
