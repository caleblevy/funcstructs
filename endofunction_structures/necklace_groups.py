from PADS import IntegerPartitions


from . import multiset
from . import rings
from . import levypartitions
from . import necklaces

def cwr_count(n, r):
    """Returns nCk(n+r-1, n-1) optimized for large n and small r."""
    val = 1
    for i in range(1, r+1):
        val *= n + r - i
        val //= i
    return val


def count_by_period(beads):
    return necklaces.FixedContentNecklaces(beads).count_by_period()


def period_combos(beads, reps):
    """All possible combinations of periods from given counts by period"""
    counts = count_by_period(beads)
    periods = [i for i, val in enumerate(counts) if val]
    for part in levypartitions.max_length_partitions(reps, len(periods)):
        for combo in rings.multisets_with_multiplicities(periods, part):
            yield combo


def period_combo_count(counts, combo):
    """Number of necklaces from a combination of periods"""
    val = 1
    for period, mult in combo.items():
        val *= cwr_count(counts[period], mult)
    return val

def necklace_groups_by_period_combo(beads, reps):
    counts = count_by_period(beads)
    """Return generator yield pairs of period groups and their counts"""
    for combo in period_combos(beads, reps):
        yield combo, period_combo_count(counts, combo)

nn2 = [1]*4 + [2]*4 + [3]*4
nn = [0]*24 + [1]*36

for ng in necklace_groups_by_period_combo(nn, 4):
    print ng
print sum(i for _, i in necklace_groups_by_period_combo(nn, 4))
print cwr_count(necklaces.FixedContentNecklaces(nn).cardinality(), 4)


def period_combo_partitions(combo):
    for val, mult in  combo.items():
        for part in levypartitions.max_length_partitions(r, n):
            _, mults = multiset.Multiset(part).split()
            yield mults

