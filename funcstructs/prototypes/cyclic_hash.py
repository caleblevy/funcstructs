"""Module for prototyping a linear time sequence hasher with cyclic invarience.

Caleb Levy, 2015.
"""


# In order to hash a cycle, we must recreate CPython's
import sys

_PyHASH_MULTIPLIER = 0xf4243  # Include/pyhash.h


class A(tuple):
    def __hash__(seq):
        """Pure python implementation of Objects/tupleobject.c tuplehash."""
        MAX = sys.maxsize
        MASK = 2 * MAX + 1
        x = 0x345678
        mult = _PyHASH_MULTIPLIER
        l = len(seq)
        for elem in seq:
            y = hash(elem) & MASK
            x = (x ^ y) & MASK
            x *= mult
            x &= MASK
            l -= 1
            mult += 82520 + 2*l
            mult &= MASK
        x += 97531
        return x & MASK


if __name__ == '__main__':
    a = (1, 2, 3, 4, 5, -1)
    print(hash(a))
    print(hash(A(a)))
