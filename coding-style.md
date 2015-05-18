Coding style for endofunction-structures

- All code is pep8
    * This means the following command produces *NO* output:

            pep8 funcstructs

    * This **DOES INCLUDE** the 79 character per line limit (newlines count).
    * Unit tests also must be pep8

- All code is python2.7 and 3.x compatible, where x is latest version

    * This means both of the following should produce no errors or warnings

            python2 funcstructs/test_runner.py
            python3 funcstructs/test_runner.py

- All classes are new style, either implicitly or explicitly:

    **Good**

        class A(object):
            pass

    **Bad**

        class A:
            pass
