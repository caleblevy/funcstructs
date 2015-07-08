README
######

:Author: Caleb Levy (caleb.levy@berkeley.edu)
:Copyright: 2012-2015 Caleb Levy
:License: MIT License
:Project Homepage: https://github.com/caleblevy/funcstructs

This is ``Funcstructs``, a collection of algorithms and data structures
implemented in Python for exploring combinatorial problems involving
endofunction structures.

Most data structures have been tested against Python 2.7, Python 3.4, Jython
2.7.0, PyPy 2.7 and PyPy 3.2. Some functionality requires numpy and matplotlib.


Available Data Structures
=========================

The key data structures are found in ``funcstructs.structures``.


Multisets
---------
Multiset
    A **multiset** is a mapping from a set into the positive integers.
    ``Multiset`` is an immutable and hashable ``frozendict`` supporting the
    same binary operations as ``collections.Counter``.

Usage
~~~~~

.. code:: python

    >>> from funcstructs.structures import Multiset
    >>> a = Multiset("abracadabra")
    >>> b = Multiset({'a': 4, 'k': 1, 'z': 1, 'm': 1, 'l': 1})
    >>> a
    Multiset({'a': 5, 'r': 2, 'b': 2, 'c': 1, 'd': 1})


    >>> a & b                           # Multiset supports the same binary
    Multiset({'a': 4})                  # operations as Counter

    >>> a - b
    Multiset({'r': 2, 'b': 2, 'a': 1, 'c': 1, 'd': 1})


Rooted Trees
------------
RootedTree
    Represents unlabelled, *un*ordered trees as a multiset of subtrees.
LevelSequence
    A **level sequence** represents an unlabelled, *ordered* tree by listing
    the heights of its nodes in depth-first traversal order. ``LevelSequence``
    inherits from ``tuple``.
DominantSequence
    A canonicalized level sequence which is lexicographically larger than the
    level sequences of all other ordered trees with the same unordered
    structure. Two level sequences correspond to the same unordered rooted tree
    if and only if they have the same ``DominantSequence``.

The ``rootedtrees`` module additionally provides three enumerators:

TreeEnumerator
    Generates the dominant sequence of each unordered rooted tree on a fixed
    number of nodes using the algorithm provided by T. Beyer and S. M.
    Hedetniemi in "Constant time generation of rooted trees."
ForestEnumerator
    Generates every **forest** (a multiset of rooted trees) on a fixed number
    of nodes.
PartitionForests
    Enumerates forests whose nodes are divided amongst trees with sizes of a
    given partition.

Usage
~~~~~

.. code:: python

    >>> from funcstructs.structures import (
    ...     RootedTree, LevelSequence, DominantSequence, TreeEnumerator,
    ...     ForestEnumerator, PartitionForests
    ... )

    >>> o1 = OrderedTree([0, 1, 1, 2, 2, 3])
    >>> o2 = OrderedTree([0, 1, 2, 2, 3, 1])
    >>> o1 == o2
    False

    >>> d = DominantSequence(o1)
    >>> d
    DominantSequence([0, 1, 2, 3, 2, 1])
    >>> d == DominantSequence(o2)
    True

    >>> RootedTree.from_levels(d)
    RootedTree({{{{}}, {}}, {}})

    >>> for d in TreeEnumerator(4):
    ...     print(RootedTree.from_levels(d))
    ...
    RootedTree({{{{}}}})
    RootedTree({{{}^2}})
    RootedTree({{{}}, {}})
    RootedTree({{}^3})



Functions
---------

Classes in the ``functions`` module represent *mathematical* **functions**:
correspondences between sets. A ``Function`` object is an associative array
which maps the set of its *keys* a set of *values*. Functions objects may be
composed using the standard multiplication syntax and are evaluated by calling.

``Endofunction`` is a Function subclass whose objects' values are a subset
of their keys. These can be iterated to produce functional digraphs, the
unlabelled versions of which are endofunction structures. These graphs consist
of rooted trees connected in cycles. 

Invertible functions are represented by ``Bijection`` objects, all of which
possess an inverse method.

``Permutations`` are invertible self-maps inheriting from both Endofunction and
Bijection. They accept negative exponents and may be used to form an algebra.

The functions module also provides *enumerators* of **functions**
(``Mappings``), **bijections** (``Isomorphisms``), **endofunctions**
(``TransformationMonoid``) and **permutations** (``SymmetricGroup``), and
convenience generators of random Function objects.


Necklaces
---------

A **necklace** is the lexicographically smallest rotation of a given "word".
For us a word is any tuple of comparable elements. Necklaces are represented by
the ``Necklace`` class, which canonicalizes any input iterable in linear time.
They are the canonical representatives of cyclic objects.


The ``necklace`` module also provides an enumerator of necklaces with a fixed
multiset of elements using the algorithm described by Joe Sawada in "A fast
algorithm to generate necklaces with fixed content."


Endofunction Structures
-----------------------

An endofunction structure is the result of removing the labels from a
functional digraph; they are the "unlabelled" version Functions. ``Funcstruct``
objects represent endofunction structures as a multiset of necklaces whose
elements are dominant sequences.

Funcstruct accepts any Endofunction object as input and returns the
corresponding structure. Two endofunctions have the same structure if and only
if the graph of one can be relabelled to look like the other.

The ``conjstructs`` module additionally provides a Funcstruct enumerator,
``EndofunctionStructures``, which can be restricted to structures with a given
cycle type.


Additional Modules
------------------

``funcstruct.structures`` contains a ``labellings`` module for enumerating
unique labels of unlabelled structures, and ``funcdists`` for computing various
statistical properties of endofunction distributions.

Note that using funcdists requires ``numpy``.


Usage
=====

.. code:: python

    >>> from funcstructs.structures import *


Additional Modules
==================

Funcstructs contains 4 ancillary modules:

- **bases**: convenience classes used to build the core data structures. These
  include

  * ``frozendict``, an immutable dictionary
  * ``Tuple``, a convenience wrapper for subclassing the builtin ``tuple``
  * ``Enumerable``, a custom abstract base class for reusable generators. It is
    an instance of ``ParamMeta``, a metaclass for adding ``__slots__`` to
    classes using the parameters of their ``__init__`` methods.

  All three account for type when testing equality, thus instances of distinct
  subclasses will not compare equal, even with the same values.

- **graphs**: objects useful for computational geometry. Currently provides a
  ``Point`` and ``Coordinates`` type for representing isolated and ordered
  groups of points in the 2D Cartesian coordinate plane, respectively. Also
  contains ``Line`` class for handling line segments.

  This package will hopefully become a small package to automate making pretty
  plots of functional digraphs.

  Requires ``numpy`` and ``matplotlib``.

- **prototypes**: ideas under development. Prototype modules may graduate to
  other parts of the project, or can disappear entirely. This package changes
  regularly, thus its contents are not summarized.

  Currently requires ``numpy`` and ``matplotlib``.

- **utils**: supporting utilities. Includes basic functions for prime
  factorization, combinatorics and iterating over subsequences.
