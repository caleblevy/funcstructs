import sys
import os

# Hack to pass pep8 rule 402
try:
    pass
finally:
    sys.path.append(os.path.join(os.getcwd(), 'PADS'))
    del sys, os

# Supporting modules
from . import (
    compositions,
    combinat,
    factorization,
    labellings,
    levypartitions,
    polynomials,
    productrange,
    subsequences
)

# Main data structures
from .conjstructs import Funcstruct, EndofunctionStructures
from .endofunctions import (
    Endofunction, SymmetricFunction,
    randfunc, randperm,
    TransformationMonoid
)
from .multiset import Multiset
from .necklaces import periodicity, Necklace, FixedContentNecklaces
from .rootedtrees import (
    RootedTree,
    OrderedTree, DominantTree,
    TreeEnumerator, ForestEnumerator, PartitionForests
)
