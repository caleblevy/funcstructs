"""Benchmarking different ways of calling dict methods.

This is crucial since we want to minimize to the extent possible the
retrieval time for frozendict methods.
"""

# We already know from "Why are explicit calls to magic methods slower than
# 'sugared' syntax?" at http://stackoverflow.com/q/22940769/3349520 that
# calling operators is much faster than anything else.

from __future__ import print_function

import timeit

define_dict = "d = {'a': 1, 'b': 2}; "

# Testing dict.items
# ------------------
itemviewer = getattr(dict, 'viewitems', dict.items).__name__  # Py 2/3 compat
setup = define_dict + "dv = dict.%s" % itemviewer

items_instance_lookup = """\
for i in range(1000):
    v = d.%s()
""" % itemviewer

items_type_lookup = """
for i in range(1000):
    v = dict.%s(d)
""" % itemviewer

items_memoized_lookup = """
for i in range(1000):
    v = dv(d)
"""

print("dict.items:")
print("-----------")
print(
    "instance lookup:",
    min(timeit.repeat(items_instance_lookup, setup, number=1000, repeat=20))
)
print(
    "type lookup:",
    min(timeit.repeat(items_type_lookup, setup, number=1000, repeat=20))
)
print(
    "memoized type lookup:",
    min(timeit.repeat(items_memoized_lookup, setup, number=1000, repeat=20))
)
print()


# Testing dict.__iter__
setup = define_dict + "di = dict.__iter__"

direct_iter = """\
for i in range(1000):
    result = iter(d)
"""

iter_method_call = """\
for i in range(1000):
    result = d.__iter__()
"""

iter_type_lookup = """\
for i in range(1000):
    result = dict.__iter__(d)
"""

iter_memoized_lookup = """\
for i in range(1000):
    result = di(d)
"""

print("dict.__iter__:")
print("--------------")
print(
    "direct call:",
    min(timeit.repeat(direct_iter, setup, number=1000, repeat=20))
)
print(
    "method lookup:",
    min(timeit.repeat(iter_method_call, setup, number=1000, repeat=20))
)
print(
    "type lookup:",
    min(timeit.repeat(iter_type_lookup, setup, number=1000, repeat=20))
)
print(
    "memoized type lookup:",
    min(timeit.repeat(iter_memoized_lookup, setup, number=1000, repeat=20))
)
