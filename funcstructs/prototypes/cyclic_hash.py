"""Module for prototyping a linear time sequence hasher with cyclic invarience.

Caleb Levy, 2015.
"""

import sys


def tuplehash(seq):
    """Pure python implementation of "tuplehash" from Objects/tupleobject.c"""
    MAX = sys.maxsize
    MASK = 2 * MAX + 1
    x = 0x345678
    mult = 0xf4243  # from "_PyHASH_MULTIPLIER" in "Include/pyhash.h"
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


def z_values(string):
    """Linear time algorithm to find all Z-values of a string."""
    # Source code copied directly from answer to "Z-Algorithm for pattern
    # matching in strings" at http://codereview.stackexchange.com/a/53969.
    n = len(string)
    z = [0] * n
    zbox_l, zbox_r, z[0] = 0, 0, n
    for i in range(1, n):
        if i < zbox_r:  # i is within a zbox
            k = i - zbox_l
            if z[k] < zbox_r - i:
                z[i] = z[k]  # Full optimization
                continue
            zbox_l = i  # Partial optimization
        else:
            zbox_l = zbox_r = i  # Match from scratch
        while zbox_r < n and string[zbox_r - zbox_l] == string[zbox_r]:
            zbox_r += 1
        z[i] = zbox_r - zbox_l
    return z


if __name__ == '__main__':
    a = (1, 2, 3, 4, 5, -1)
    print(hash(a))
    print(tuplehash(list(a)))
    print(z_values("aaabcaaababaaabcdaba"))
