Funcstructs
###########

A Python library for dealing with endofunction structures and related
combinatorial objects.

Funcstructs has been tested on Python and PyPy versions 2.7 and 3.2+,
Jython 2.7 and Pythonista for iOS.


Data Structures
===============

**Multisets**

- ``Multiset``: An immutable mapping from a set into the positive integers
  supporting the same binary operations as ``collections.Counter``.


**Rooted Trees**

- ``RootedTree``: An unlabelled, unordered tree represented as a multiset of
  subtrees.
- ``LevelSequence``: An unlabelled *ordered* tree represented by listing the
  height of each node above the root in a pre-ordered depth-first traversal.
- ``DominantSequence``: The lexicographically maximal level sequence of all
  orderings of a RootedTree object.
- ``TreeEnumerator``: Generates the dominant sequence of each unordered rooted
  tree on a fixed number of nodes using the algorithm provided by T. Beyer and
  S. M. Hedetniemi in "Constant time generation of rooted trees."


**Necklaces**

- ``Necklace``: The lexicographically smallest rotation of a sequence of
  totally ordered elements. They are the canonical representatives of cycles.
- ``FixedContentNecklaces``: Enumerator of necklaces with a fixed multiset of
  elements using the `simple fixed content` algorithm described by Joe Sawada
  in "A fast algorithm to generate necklaces with fixed content."


**Functions** (in type/enumerator pairs)

- ``Function``/``Mappings``: A mathematical correspondence between sets
  represented with an associative array.
- ``Endofunction``/``TransformationMonoid``: A Function whose domain and
  codomain are equal.
- ``Bijection``/``Isomorphisms``: An invertible Function.
- ``Permutation``/``SymmetricGroup``: A Bijective Endofunction.


**Endofunction Structures**

- ``ConjugacyClass``: Represents a conjugacy class of Endofunctions as a
  multiset of necklaces whose elements are dominant sequences.
- ``Funcstructs``: Enumerates endofunction structures on a fixed
  number of nodes, optionally restricted to a given cycle type.


Usage
=====
.. code:: python

    >>> from funcstructs import *

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
    >>> ConjugacyClass(f) == ConjugacyClass(g)
    True

    >>> p = Permutation({0: 3, 1: 4, 2: 1, 3: 0, 4: 2})
    >>> p**-2
    Permutation({0: 0, 1: 4, 2: 1, 3: 3, 4: 2})
    >>> p**3 == p * p * p
    True


Additional Modules
==================

- **bases**: Convenience classes used to build the core data structures. These
  include ``frozendict``, and immutable dictionary, and ``Enumerable``, a
  parametrized abstract base class for reusable generators.
- **graphs**: Computational geometry primitives. Intended to become an
  automated pretty-plot maker for endofunction structure graphs. *Requires
  numpy and matplotlib.*
- **prototypes**: Dumping ground for unrefined ideas under development.
- **utils**: Supporting utilities. Includes basic functions for prime
  factorization, combinatorics and iterating over subsequences.


About
=====
:Author: Caleb Levy (caleb.levy@berkeley.edu)
:Copyright: 2012-2015 Caleb Levy
:License: MIT License
:Project Homepage: https://github.com/caleblevy/funcstructs
