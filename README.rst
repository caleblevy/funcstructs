FUNCSTRUCTS
###########

A collection of algorithms and data structures implemented in Python for
exploring combinatorial problems involving endofunction structures.


Features
========
- All data structures in ``funcstructs`` are immutable and hashable
- Code is thoroughly tested: about 1/3 to 1/2 of project is tests
- Works on many implementations: Python 2.7, 3.4, PyPy 2.7, 3.2 and Jython 2.7.
- Contains several original algorithms you won't find anywhere else.


Overview
========
The following data structures are available in ``funcstructs.structures``:

Multisets
---------
``Multiset``
    A **multiset** is a mapping from a set into the positive integers.
    ``Multiset`` is an immutable and hashable ``frozendict`` supporting the
    same binary operations as ``collections.Counter``.


Rooted Trees
------------
``RootedTree``
    Represents unlabelled, *un*\ ordered trees as a multiset of subtrees.
``LevelSequence``
    A **level sequence** represents an unlabelled, *ordered* tree by listing
    the heights of its nodes above the root, in depth-first traversal order.
    ``LevelSequence`` inherits from ``tuple``.
``DominantSequence``
    A canonicalized level sequence which is lexicographically larger than the
    level sequences of all other ordered trees with the same unordered
    structure. Two level sequences correspond to the same unordered rooted tree
    if and only if they have the same dominant sequence.
``TreeEnumerator``
    Generates the dominant sequence of each unordered rooted tree on a fixed
    number of nodes using the algorithm provided by T. Beyer and S. M.
    Hedetniemi in "Constant time generation of rooted trees."


Necklaces
---------

``Necklace``
    A **necklace** is the lexicographically smallest rotation of a given word.
    For us a word is any tuple of comparable elements. ``Necklace`` accepts an
    iterable as input, and raises an error when the elements are not orderable,
    and otherwise returns the tuple of the smallest rotation. ``Necklace``
    objects are the canonical representatives of cycles.
``FixedContentNecklaces``
    Enumerator of necklaces with a fixed multiset of elements using the 
    `simple fixed content` algorithm described by Joe Sawada in "A fast
    algorithm to generate necklaces with fixed content."


Functions
---------

``Function``
    Mathematical **functions** are correspondences between sets. A ``Function``
    object is an associative array which maps the set of its *keys* to the set
    of *values*. Function may be composed using the standard multiplication.
``Endofunction``
    A ``Function`` whose values are a subset of its keys. They can be iterated
    to produce functional digraphs consisting of rooted trees connected in
    cycles.
``Bijection``
    An invertible ``Function``.
``Permutation``
    A bijective endofunction. They accept negative exponents.

The functions module also provides enumerators corresponding to each of the
``Function`` types above:

- ``Mappings``
- ``Isomorphisms``
- ``TransformationMonoid``
- ``SymmetricGroup``


Endofunction Structures
-----------------------
``Funcstruct``
    An **endofunction structure** is the result of removing the labels from a
    functional digraph. They are conjugacy classes of transformation monoids.
    ``Funcstruct`` objects represent endofunction structures as a multiset of
    necklaces whose elements are dominant sequences.

    Funcstruct accepts any Endofunction object as input and returns the
    corresponding structure. Two endofunctions have the same structure if and
    only if the graph of one can be relabelled to look like the other.
``EndofunctionStructures``
    Enumerator of endofunction structures using a given number of nodes. Can
    optionally specify a cycle type. As far as I am aware, this algorithm is
    original to the ``funcstructs`` library.


Labellings
----------
Functions for enumerating unique labellings of unlabelled structures. Includes
functions for dealing with set partitions. These are found in
``funcstructs.structures.labellings``.

Function Distributions
----------------------
Functions for computing various statistical properties of endofunction
distributions. These are found in ``funcstructs.structures.funcdists``.

**Note**: using ``funcdists`` requires ``numpy``.


Additional Modules
==================

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

  This package will hopefully expand into a small package to automate making
  pretty plots of functional digraphs.

  Requires ``numpy`` and ``matplotlib``.

- **prototypes**: ideas under development. Prototype modules may graduate to
  other parts of the project, or can disappear entirely. This package changes
  regularly, thus its contents are not summarized.

  Currently requires ``numpy`` and ``matplotlib``.

- **utils**: supporting utilities. Includes basic functions for prime
  factorization, combinatorics and iterating over subsequences.


About
=====

:Author: Caleb Levy (caleb.levy@berkeley.edu)
:Copyright: 2012-2015 Caleb Levy
:License: MIT License
:Project Homepage: https://github.com/caleblevy/funcstructs
