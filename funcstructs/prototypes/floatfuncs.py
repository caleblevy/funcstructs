"""Module for computing conjugacy classes of self mappings on floating point
numbers.

Caleb Levy, 2015.
"""

import numpy as np

from funcstructs.structures import Endofunction


class NanType(np.float16):
    __slots__ = ()

    def __new__(cls):
        return np.float16.__new__(cls, 'nan')

    def __eq__(self, other):
        return isinstance(other, np.float16) and np.isnan(other)

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return 0


NaN = NanType()
Inf = np.float16('inf')
Max16 = np.float16(65504.0)
Min16 = -Max16
Zero = np.float16(0)
One = np.float16(1)


Negative = {-Inf}
f = Min16
while f < Zero:
    Negative.add(f)
    f = np.nextafter(f, Inf, dtype=np.float16)
del f

Negative = frozenset(Negative)
Positive = frozenset(-x for x in Negative)
NonPositive = Negative.union({Zero})
NonNegative = Positive.union({Zero})
NonNan = Negative.union(NonNegative)
Finite = NonNan - {-Inf, Inf}
UnitInterval = frozenset(x for x in NonNegative if x <= 1)
Floats = NonNan.union({NaN})


def floatfunc(func, domain=Floats):
    """Return a mapping on the domain from func."""
    pairs = []
    for x in domain:
        y = func(x)
        if np.isnan(y):
            y = NaN  # Absorb non-canonical NaNs.
        pairs.append((x, y))
    return Endofunction(pairs)
