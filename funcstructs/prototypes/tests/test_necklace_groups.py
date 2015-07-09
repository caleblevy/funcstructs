import unittest

from funcstructs.utils import combinat
from funcstructs.prototypes.necklace_groups import (
    count_by_period,
    necklace_groups_by_period_combo
)


class NecklaceGroupTests(unittest.TestCase):

    def test_necklace_group_by_period_combo_counts(self):
        necks = [[1]*4+[2]*4+[3]*4, [0]*24+[1]*36]
        for n in necks:
            self.assertEqual(
                combinat.nCWRk(sum(count_by_period(n)), 4),
                sum(i for _, i in necklace_groups_by_period_combo(n, 4))
            )
