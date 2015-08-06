"""Methods for counting function calls.

Caleb Levy, 2015.
"""

from __future__ import print_function

from functools import wraps


class CallCounter(object):
    """CallCounter(name) -> a new call counter with given name

    Return a call counting object. Whenever a CallCounter is called, it
    will print its name and the number of times it has been called.

    >>> c1 = CallCounter("c1")
    >>> c2 = CallCounter("c2")
    >>> c1(); c1(); c2(); c2(); c1()
    """

    def __init__(self, name):
        self.name = str(name)
        self._callcount = 0

    def __call__(self):
        self._callcount += 1
        print(self.name+":", self._callcount)


def callcounted(func):
    """Function decorator which makes a function print how many times
    it has been called at each call.
    """
    counter = CallCounter(func.__name__)

    @wraps(func)
    def counted_func(*args, **kwargs):
        counter()
        return func(*args, **kwargs)

    return counted_func
