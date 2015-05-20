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
    conjstructs,
    funcdists,
    functions,
    labellings,
    multiset,
    necklaces,
    productrange,
    rootedtrees,
    subsequences
)

# Main data structures
from .conjstructs import Funcstruct, EndofunctionStructures
from .functions import (
    Function, Bijection, Endofunction, SymmetricFunction,
    rangefunc, rangeperm, randfunc, randperm, randconj,
    TransformationMonoid
)
from .multiset import Multiset, unordered_product
from .necklaces import periodicity, Necklace, FixedContentNecklaces
from .rootedtrees import (
    OrderedTree, DominantTree, RootedTree,
    TreeEnumerator, ForestEnumerator, PartitionForests
)
