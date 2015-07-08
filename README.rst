README
######

This is ``Funcstructs``, a collection of algorithms and data structures
implemented in Python for exploring combinatorial problems involving
endofunction structures.

Most data structures have been tested against Python 2.7, Python 3.4, Jython
2.7.0, PyPy 2.7 and PyPy 3.2. Some functionality requires numpy and matplotlib.


Overview
========

``Funcstructs`` is broken into 5 main submodules:

- **bases**: convenience classes used to build the main data structures. These
  include

  * ``frozendict``, an immutable dictionary
  * ``Tuple``, a convenience wrapper for subclassing the builtin tuple
  * ``Enumerable``, a custom abstract base class for reusable generators

- **graphs**: objects representing points and coordinates. This will one day
  become an automated graph drawing package.
- **prototypes**: ideas under development. Some of these may one day move into
  ``structures``, and some may be abandoned.
- **structures**: the main data structures, outlined below.
- **utils**: Supporting utilities.


Available Data Structures
=========================

To be written


Usage
=====

.. code:: python

    >>> from funcstructs.structures import *


:Author: Caleb Levy (caleb.levy@berkeley.edu)
:Copyright: 2012-2015 Caleb Levy
:License: MIT License
:Project Homepage: https://github.com/caleblevy/funcstructs