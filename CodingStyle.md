Coding style for endofunction-structures

- All code is pep8
    * This means the following command produces *NO* output:

            pep8 --exclude=PADS,untracked .

    * This **DOES INCLUDE** the 79 character per line limit (newlines count).
    * In general *some* code produced this way *may* look slightly uglier, but
      code style is not *everything*. A simple guideline for checking style is nice to have.
    * This does *not* necessarily cover variable names (class names are
      CapitolCamelCase)
    * This includes unit tests

- All code is python2.7 and 3.x compatible, where x is latest version

    * This means both of the following should produce no errors or warnings

            python2 -m unittest discover
            python3 -m unittest discover

    * The module `six` is not allowed; dependencies should be minimized
    * **NO USING** `if sys.version[0] > 2:` clauses
    * No `xrange`

- All classes are explicitly new style

    **Good**

        class A(object):
            pass

    **Bad**

        class A:
            pass


- Imports 
    * Modules in endofunction_structures/ have the following style:

        **Good**

            import mod1
            from . import submod2
            from mod3 import *  # (Only if module has __all__)

        **Bad**

            from mod1 import func1, func2, Class1, const
    
    * Exception: long, deeply nested imports

            from sympy.utilities.iterables import multiset_partitions

    * Unit tests, and modules in prototyping, funcgraphs need not be so strict