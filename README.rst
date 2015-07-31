FUNCSTRUCTS
###########

A collection of algorithms and data structures implemented in Python for
exploring combinatorial problems involving endofunction structures.

Tested on Python 2.7 and 3.4, PyPy 2.7 and 3.2, and Jython 2.7.


Available Data Structures
=========================

**Multisets**

- ``Multiset``: A mapping from a set into the positive integers. It is an
  immutable and hashable ``frozendict`` supporting the same binary operations
  as ``collections.Counter``.


**Rooted Trees**

- ``RootedTree``: An unlabelled, unordered tree represented as a multiset of
  subtrees.
- ``LevelSequence``: An unlabelled *ordered* tree represented by listing the
  height of each node above the root in a pre-ordered depth-first traversal.
- ``DominantSequence``: A canonical level sequence which is lexicographically
  larger than the level sequences of all other ordered trees with the same
  unordered structure. Two level sequences correspond to the same unordered
  rooted tree if and only if they have the same dominant sequence.
- ``TreeEnumerator``: Generates the dominant sequence of each unordered rooted
  tree on a fixed number of nodes using the algorithm provided by T. Beyer and
  S. M. Hedetniemi in "Constant time generation of rooted trees."


**Necklaces**

- ``Necklace``: A **necklace** is the lexicographically smallest rotation of a
  given word. For us a word is any tuple of comparable elements. ``Necklace``
  accepts an iterable as input, and raises an error when the elements are not
  orderable, and otherwise returns the tuple of the smallest rotation.
  ``Necklace`` objects are the canonical representatives of cycles.
- ``FixedContentNecklaces``: Enumerator of necklaces with a fixed multiset of
  elements using the `simple fixed content` algorithm described by Joe Sawada
  in "A fast algorithm to generate necklaces with fixed content."


**Functions**

- ``Function``: Mathematical **functions** are correspondences between sets. A
  ``Function`` object is an associative array which maps the set of its *keys*
  to the set of *values*. Function may be composed using the standard
  multiplication.
- ``Endofunction``: A ``Function`` whose values are a subset of its keys. They
  can be iterated to produce functional digraphs consisting of rooted trees
  connected in cycles.
- ``Bijection``: An invertible ``Function``.
- ``Permutation``: A bijective endofunction. They accept negative exponents.

The functions module also provides enumerators corresponding to each of the
``Function`` types above:

- ``Mappings``
- ``Isomorphisms``
- ``TransformationMonoid``
- ``SymmetricGroup``

**Endofunction Structures**

- ``Funcstruct``: A conjugacy class of a transformation monoid represented by a
  multiset of necklaces whose elements are dominant sequences. Accepts any
  Endofunction as input.
- ``EndofunctionStructures``: Enumerates endofunction structures on a fixed
  number of nodes (and those with a fixed cycle type). Algorithm derived by
  Caleb Levy.


**Labellings**

Functions for enumerating unique labellings of unlabelled structures. Includes
functions for dealing with set partitions. These are found in
``funcstructs.structures.labellings``.


**Function Distributions**

Functions for computing various statistical properties of endofunction
distributions. These are found in ``funcstructs.structures.funcdists``.

**Note**: using ``funcdists`` requires ``numpy``.


Usage
=====
.. code:: python

    >>> from funcstructs.structures import *

    # --------- #
    # Multisets #
    # --------- #

    >>> a = Multiset("abra")
    >>> b = Multiset("cadabra")
    >>> sorted(a + b)
    ['a', 'a', 'a', 'a', 'a', 'b', 'b', 'c', 'd', 'r', 'r']

    >>> a & b
    Multiset({'a': 2, 'r': 1, 'b': 1})

    # ------------ #
    # Rooted Trees #
    # ------------ #

    >>> o = LevelSequence([0, 1, 1, 2, 2, 3])
    >>> d = DominantSequence(o)
    >>> d == DominantSequence([0, 1, 1, 2, 3, 2])
    True
    >>> d
    DominantSequence([0, 1, 2, 3, 2, 1])

    >>> for t in TreeEnumerator(4):
    ...   print(list(t), RootedTree(t))
    ...
    [0, 1, 2, 3] RootedTree({{{{}}}})
    [0, 1, 2, 2] RootedTree({{{}^2}})
    [0, 1, 2, 1] RootedTree({{{}}, {}})
    [0, 1, 1, 1] RootedTree({{}^3})

    # --------- #
    # Necklaces #
    # --------- #

    >>> Necklace("cabcab")
    'abcabc'
    >>> Necklace("abc") == Necklace("bca") == Necklace("cab")
    True
    >>> periodicity([1, 2, 3, 1, 1, 2, 3, 1])
    4
    >>> for n in FixedContentNecklaces(multiplicities=(3, 3)):
    ...   print(list(n))
    ...
    [0, 0, 0, 1, 1, 1]
    [0, 0, 1, 0, 1, 1]
    [0, 0, 1, 1, 0, 1]
    [0, 1, 0, 1, 0, 1]

    # --------- #
    # Functions #
    # --------- #

    >>> s = Bijection(a=1, b=2, c=3)
    >>> s.inverse
    Bijection({1: 'a', 2: 'b', 3: 'c'})
    >>> s == s.inverse.inverse
    True

    >>> f = Endofunction({1: 1, 2: 1, 3: 3})
    >>> g = s.inverse.conj(f)
    >>> list(g)
    [('a', 'a'), ('c', 'c'), ('b', 'a')]
    >>> Funcstruct(f) == Funcstruct(g)
    True

    >>> p = Permutation({0: 3, 1: 4, 2: 1, 3: 0, 4: 2})
    >>> p**-2
    Permutation({0: 0, 1: 4, 2: 1, 3: 3, 4: 2})
    >>> p**3 == p * p * p
    True


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
