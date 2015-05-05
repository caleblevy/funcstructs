Coding style for endofunction-structures

- All code is pep8
    * This means the following command produces *NO* output:

            pep8 . --exclude=PADS,untracked

    * This **DOES INCLUDE** the 79 character per line limit (newlines count).
    * Unit tests also must be pep8

- All code is python2.7 and 3.x compatible, where x is latest version

    * This means both of the following should produce no errors or warnings

            python2 test_runner.py
            python3 test_runner.py

    * The module **six** is not allowed; dependencies should be minimized

- All classes are explicitly new style, or inherit from new style classes:

    **Good**

        class A(object):
            pass

    **Bad**

        class A:
            pass
