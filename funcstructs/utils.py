"""Small utility functions and convenience wrappers.

Caleb Levy, 2015.
"""

import functools
import itertools
import operator


def flatten(lol):
    """Flatten a list of lists."""
    return itertools.chain.from_iterable(lol)


def prod(iterable):
    """Product of all items in an iterable."""
    return functools.reduce(operator.mul, iterable, 1)


# Modification of werkzeug.cached_property. Here we have chosen not to
# implement a setter for stronger interface guarantees that the properties will
# not change.
class cached_property(property):

    """A decorator that converts a function into a lazy property.  The
    function wrapped is called the first time to retrieve the result
    and then that calculated result is used the next time you access
    the value::
        class Foo(object):
            @cached_property
            def foo(self):
                # calculate something important here
                return 42
    The class has to have a `__dict__` in order for this property to
    work.
    """

    # implementation detail: A subclass of python's builtin property
    # decorator, we override __get__ to check for a cached value. If one
    # choses to invoke __get__ by hand the property will still work as
    # expected because the lookup logic is replicated in __get__ for
    # manual invocation.

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        if self.fget.__name__ not in obj.__dict__:
            obj.__dict__[self.fget.__name__] = self.fget(obj)
        return obj.__dict__[self.fget.__name__]
