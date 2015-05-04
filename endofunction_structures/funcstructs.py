"""Algorithms and data structures for endofunction structures: conjugacy
classes of the transformation monoid, represented by directed graphs with nodes
of outdegree one.

Caleb Levy, 2014 and 2015.
"""

import fractions
import itertools

import numpy as np

from . import (
    bases,
    compositions,
    counts,
    endofunctions,
    factorization,
    levypartitions,
    multiset,
    necklaces,
    productrange,
    rootedtrees,
    subsequences
)


def _flatten(lol):
    """Flatten a list of lists."""
    return list(itertools.chain.from_iterable(lol))


def _chunks(l, n):
    """ Yield successive n-sized chunks from l. """
    for i in range(0, len(l), n):
        yield l[i:i+n]


def _indent_treestring(tree, second_indent, end):
    """Format a rooted tree string with indents. """
    treestr = str(rootedtrees.RootedTree.from_leveltree(tree))
    treestr_list = [treestr[:end]]
    for s in _chunks(treestr[end:], end-second_indent):
        treestr_list.append(' '*second_indent+s)
    return treestr_list


def _structstring(func, cycle_prefix=2, cycle_suffix=2, tree_indent=4, end=78):
    fstrs = []
    fstrs.append('\nFuncstruct:\n')
    cycle_str = ' '*cycle_prefix + 'Cycle(' + ' '*cycle_suffix
    l = len(cycle_str)
    for cycle, count in func.items():
        fstrs.append(cycle_str+'\n')
        for tree in cycle:
            for t in _indent_treestring(tree, tree_indent, end-l):
                fstrs.append(' '*l+t+'\n')
        fstrs.append(' '*(l-cycle_suffix-1)+')'+' * '+str(count)+'\n')
    return ''.join(fstrs)


class Funcstruct(multiset.Multiset):
    """ An endofunction structure may be represented as a forest of trees,
    grouped together in multisets corresponding to cycle decompositions of the
    final set (the subset of its domain on which it is invertible). The
    orderings of the trees in the multisets correspond to necklaces whose beads
    are the trees themselves. """

    def __new__(cls, cycles, precounted=True):
        if isinstance(cycles, cls):
            return cycles
        self = super(Funcstruct, cls).__new__(cls, cycles)
        if precounted is not None:
            self.n = precounted
        else:
            self.n = len(_flatten(_flatten(self)))
        return self

    @classmethod
    def from_func(cls, f):
        cycles = []
        for cycle in f.cycles:
            strand = []
            for el in cycle:
                strand.append(rootedtrees.DominantTree.from_func(f, el))
            cycles.append(necklaces.Necklace(strand))
        return cls(cycles)

    __lt__ = None

    def __repr__(self):
        return self.__class__.__name__+'(%s)' % list(self)

    def __str__(self):
        return _structstring(self)

    @property
    def degeneracy(self):
        """ The number of equivalent ways of labelling each endofunction with
        unlabelled structure self.

        The size of the conjugacy class of self is n!/self.degeneracy() """
        # First the degeneracy from the permutations of arrangements of cycles
        degeneracy = super(Funcstruct, self).degeneracy()
        # Then account for the periodcity of each cycle
        for cycle, mult in self.items():
            cycledeg = cycle.degeneracy()
            # Finally the degeneracy of each rooted tree.
            for tree in cycle:
                cycledeg *= tree.degeneracy()
            degeneracy *= cycledeg ** mult
        return degeneracy

    def func_form(self):
        """ Convert function structure to canonical form by filling in numbers
        from 0 to n-1 on the cycles and trees. """
        # Find the tree form of non-cyclic nodes
        tree_start = 0
        func = []
        for tree in itertools.chain.from_iterable(self):
            l = len(tree)
            tree_perm = range(tree_start, tree_start+l)
            func_tree = tree.labelled_sequence(tree_perm)
            func.extend(func_tree)
            tree_start += l
        # Permute the cyclic nodes to form the cycle decomposition
        cycle_start = 0
        for cycle in self:
            node_prev = node = 0
            cycle_len = len(_flatten(cycle))
            for tree in cycle:
                node += len(tree)
                func[cycle_start+node_prev] = cycle_start + (node % cycle_len)
                node_prev += len(tree)
            cycle_start += cycle_len
        return endofunctions.Endofunction(func)

    @property
    def imagepath(self):
        """ Given an endofunction structure funcstruct, compute the image path
        directly without conversion to a particular endofunction. """
        cardinalities = np.array([0]+[0]*(self.n-2), dtype=object)
        for tree in itertools.chain.from_iterable(self):
            cardinalities += 1
            for subseq in subsequences.increasing(tree):
                k = len(subseq) - 1
                k -= 1 if subseq[0] is 1 else 0
                if k > 0:
                    # Microoptimization: memoize the calls to range
                    cardinalities[:k] += range(k, 0, -1)
        return cardinalities


def direct_unordered_attachments(t, l):
    """Enumerate the ways of directly attaching t unlabelled free nodes to l
    unlabelled nodes."""
    return levypartitions.fixed_length_partitions(t+l, l)


def attachment_forests(t, l):
    """Enumerate all ways to make rooted trees from t free nodes and attach
    them to a a cycle of length l."""
    for partition in direct_unordered_attachments(t, l):
        for forest in rootedtrees.PartitionForests(partition):
            for necklace in necklaces.FixedContentNecklaces(forest):
                yield necklace


def component_groups(c, l, m):
    """ Enumerate ways to make rooted trees from c free nodes and attach them
    to a group of m cycles of length l. """
    for partition in direct_unordered_attachments(c, m):
        for cycle_group in productrange.unordered_product(
                partition,
                lambda y: attachment_forests(y-1, l)):
            yield cycle_group


def cycle_type_funcstructs(n, cycle_type):
    """ Enumerate all funcstructs on n nodes corresponding to a give cycle
    type. """
    treenodes = n - sum(cycle_type)
    lengths, multiplicities = cycle_type.split()
    l = len(lengths)
    for composition in compositions.weak_compositions(treenodes, l):
        cycle_groups = []
        for c, l, m in zip(composition, lengths, multiplicities):
            cycle_groups.append(component_groups(c, l, m))
        for bundle in itertools.product(*cycle_groups):
            yield Funcstruct(itertools.chain.from_iterable(bundle), n)


def funcstruct_enumerator(n):
    """Enumerate endofunction structures on n elements. Equalivalent to all
    conjugacy classes in TransformationMonoid(n)."""
    for i in range(1, n+1):
        for partition in levypartitions.partitions(i):
            for struct in cycle_type_funcstructs(n, partition):
                yield struct


class EndofunctionStructures(bases.Enumerable):
    """Represents the class of all endofunction structures."""

    def __init__(self, node_count, cycle_type=None):
        super(EndofunctionStructures, self).__init__(node_count, cycle_type, 0)

    def __iter__(self):
        if not self.partition:
            return funcstruct_enumerator(self.n)
        return cycle_type_funcstructs(self.n, self.partition)

    def cardinality(self):
        """Count the number of endofunction structures on n nodes. Iterates
        over the tuple representation of partitions using the formula featured
        in De Bruijn, N.G., "Enumeration of Mapping Patterns", Journal of
        Combinatorial Theory, Volume 12, 1972. See the papers directory for the
        original reference."""
        tot = 0
        for b in levypartitions.tuple_partitions(self.n):
            product_terms = []
            for i in range(1, len(b)):
                s = 0
                for j in factorization.divisors(i):
                    s += j * b[j]
                s **= b[i]
                s *= fractions.Fraction(i, 1)**(-b[i])/counts.factorial(b[i])
                product_terms.append(s)
            tot += counts.prod(product_terms)
        return int(tot)
