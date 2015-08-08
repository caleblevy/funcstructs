"""Functions for iterating over dynamically nested loops.

Caleb Levy, 2014 and 2015.
"""

from itertools import product

__all__ = ["productrange", "rev_range"]


def productrange(*ranges):
    """Cartesian product of range mapped to each of the ranges. For example,

    productrange(3, 2) --> product(range(3), range(2))
    productrange(5, (2, 10, 3)) --> product(range(5), range(2, 10, 3))
    """
    _ranges = []
    for r in ranges:
        if isinstance(r, int):
            _ranges.append(range(r))
        else:
            _ranges.append(range(*r))
    return product(*_ranges)
