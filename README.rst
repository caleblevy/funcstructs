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

Additionally, there are three enumerators:

``TreeEnumerator``
    Generates the dominant sequence of each unordered rooted tree on a fixed
    number of nodes using the algorithm provided by T. Beyer and S. M.
    Hedetniemi in "Constant time generation of rooted trees."
``ForestEnumerator``
    Generates every **forest** (a multiset of rooted trees) on a fixed number
    of nodes.
``PartitionForests``
    Enumerates forests whose nodes are divided amongst trees with sizes of a
    given partition.

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

    >>> RootedTree(d)
    RootedTree({{{{}}, {}}, {}})

    >>> for d in TreeEnumerator(4):
    ...     print(RootedTree(d))
    ...
    RootedTree({{{{}}}})
    RootedTree({{{}^2}})
    RootedTree({{{}}, {}})
    RootedTree({{}^3})


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

.. code:: python

    >>> from funcstructs.structures import Necklace, FixedContentNecklaces
    >>> n = Necklace("cabcab")
    >>> n
    Necklace(['a', 'b', 'c', 'a', 'b', 'c'])
    >>> n.period()
    3

    >>> fc = FixedContentNecklace([1, 1, 1, 2, 2, 2])
    >>> fc
    FixedContentNecklaces(elements=(1, 2), multiplicities=(3, 3))
    >>> list(fc)
    [Necklace([1, 1, 1, 2, 2, 2]), Necklace([1, 1, 2, 1, 2, 2]),
    Necklace([1, 1, 2, 2, 1, 2]), Necklace([1, 2, 1, 2, 1, 2])]
    >>> fc.count_by_period()
    [0, 1, 0, 3]


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

.. code:: python

    >>> from funcstructs.structures import (
    ...     Function, Endofunction, Bijection, Permutation,
    ...     Mappings, SymmetricGroup
    ... )
    
    >>> f = Function(a=1, b=2, c=2)                           # Function
    >>> f['a']
    1
    >>> f['b'] + f['c']
    4
    >>> g = Function({1: 'a', 2: 'a', 3: 'a'})
    >>> f * g
    Function({0: 1, 1: 1, 2: 1})
    >>> g * f
    Function({'a': 'a', 'c': 'a', 'b': 'a'})

    >>> h = Endofunction({0: 0, 1: 0, 2: 1, 3: 2, 4: 3})      # Endofunction
    >>> h.cycles()
    frozenset([(0, )])
    >>> h**3
    Endofunction({0: 0, 1: 0, 2: 0, 3: 0, 4: 1})

    >>> b = Bijection(a=1, b=2, c=3, d=4, e=5)                # Bijection
    >>> b.inverse()
    Bijection({1: 'a', 2: 'b', 3: 'c', 4: 'd', 5: 'e'})
    >>> b * b.inverse()
    Bijection({1: 1, 2: 2, 3: 3, 4: 4, 5: 5})
    >>> b.inverse() * b
    Bijection({'a': 'a', 'c': 'c', 'b': 'b', 'e': 'e', 'd': 'd'})

    >>> p = Permutation({0: 3, 1: 4, 2: 1, 3: 0, 4: 2})       # Permutation
    >>> p ** -4
    Permutation({0: 0, 1: 2, 2: 4, 3: 3, 4: 1})
    >>> set([p, p**-1, p**-2])
    set([Permutation({0: 0, 1: 4, 2: 1, 3: 3, 4: 2}),
    Permutation({0: 3, 1: 4, 2: 1, 3: 0, 4: 2}), 
    Permutation({0: 3, 1: 2, 2: 4, 3: 0, 4: 1})])

    >>> list(Mappings(2, 3))                                  # Enumerators
    [Function({0: 0, 1: 0}), Function({0: 0, 1: 1}), Function({0: 0, 1: 2}),
    Function({0: 1, 1: 0}), Function({0: 1, 1: 1}), Function({0: 1, 1: 2}),
    Function({0: 2, 1: 0}), Function({0: 2, 1: 1}), Function({0: 2, 1: 2})]

    >>> list(SymmetricGroup("abc"))
    >>> list(SymmetricGroup("abc"))
    [Permutation({'a': 'a', 'c': 'c', 'b': 'b'}),
    Permutation({'a': 'a', 'c': 'b', 'b': 'c'}),
    Permutation({'a': 'b', 'c': 'c', 'b': 'a'}),
    Permutation({'a': 'b', 'c': 'a', 'b': 'c'}),
    Permutation({'a': 'c', 'c': 'b', 'b': 'a'}),
    Permutation({'a': 'c', 'c': 'a', 'b': 'b'})]


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

.. code:: python

    >>> from funcstructs.structures import (
    ...     Endofunction, Bijection, Funcstruct, EndofunctionStructures)

    >>> f = Endofunction({0: 4, 1: 4, 2: 0, 3: 1, 4: 2, 5: 5, 6: 2, 7: 7})
    >>> Funcstruct(f)
    Funcstruct._from_cycles({
        Necklace([DominantSequence([0])]): 2,
        Necklace([
            DominantSequence([0]),
            DominantSequence([0, 1, 2]),
            DominantSequence([0, 1])
            ]): 1
        })

    >>> b = Bijection(zip(range(8), "abcdefgh"))
    >>> g = b.conj(f)
    Endofunction({'a': 'e', 'c': 'a', 'b': 'e', 'e': 'c', 'd': 'b', 'g': 'c',
    'f': 'f', 'h': 'h'})
    >>> Funcstruct(r) == Funcstruct(h)
    True

    >>> es = EndofunctionStructures(4)
    >>> len(list(es))
    >>> t = EndofunctionStructures(10, cycle_type=(2, 2, 3))
    >>> len(list(t))
    25

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
