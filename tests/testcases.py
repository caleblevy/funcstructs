"""TestCase with stronger assertions."""

import pickle
from itertools import combinations, combinations_with_replacement
from unittest import TestCase


def assertIsTrue(self, expr, msg=None):
    """Assert than an expression evaluates identically to 'True'."""
    self.assertIs(True, expr, msg)


def assertIsFalse(self, expr, msg=None):
    """Assert that an expression evaluates identically to 'False'."""
    self.assertIs(False, expr, msg)


def assertFullyEqual(self, first, second, msg=None):
    """Enhanced version of the assertEqual method for checking custom
    equality operations. Tests both that a == b and b == a, and
    that a != b and b != a evaluate 'False'.
    """
    assertIsTrue(self, first == second, msg)
    assertIsTrue(self, second == first, msg)
    assertIsFalse(self, first != second, msg)
    assertIsFalse(self, second != first, msg)


def assertFullyUnequal(self, first, second, msg=None):
    """Enhanced version of the assertNotEqual method for checking custom
    equality operations. Tests both that a != b and b != a, and that
    a == b and b == a evaluate 'False'.
    """
    assertIsFalse(self, first == second, msg)
    assertIsFalse(self, second == first, msg)
    assertIsTrue(self, first != second, msg)
    assertIsTrue(self, second != first, msg)


def assertAllEqual(self, *objects):
    """Assert all the objects are fully equal."""
    for obj1, obj2 in combinations_with_replacement(objects, 2):
        assertFullyEqual(self, obj1, obj2, msg)


def assertAllUnique(self, *objects):
    """Assert that all of the given objects are unique."""
    for obj1, obj2 in combinations(objects, 2):
        assertFullyUnequal(obj1, obj2)


def assertReprEvaluatesEqual(self, obj, msg=None):  # locals = locals, globals
    # = globals, if callable(locals): locals = locals()
    """Test repr(obj) is a valid expression returning obj."""
    r = eval(repr(obj))
    assertFullyEqual(self, obj, r, msg)
    self.assertIs(obj.__class__, r.__class__, msg)


def assertPicklable(self, obj, msg=None):
    """Test that obj is serializable and its pickle evaluates to itself."""
    p = pickle.loads(pickle.dumps(obj))
    assertFullyEqual(self, obj, p, msg)
    self.assertIs(obj.__class__, p.__class__, msg)


def assertSerializable(self, obj, msg=None):
    """Test that obj can be round-tripped both by pickling and repr-eval"""
    assertReprEvaluatesEqual(self, obj, msg)
    assertPicklable(self, obj, msg)


def assertHashable(self, obj, msg=None):
    """Test that an object is hashable."""
    try:
        hash(obj)
    except TypeError:
        self.fail("%s is not hashable" % obj)


def assertUnhashable(self, obj, msg=None):
    """Test that an object cannot be hashed."""
    with self.assertRaises(TypeError, msg="%s is hashable" % obj):
        hash(obj)


def assertSelfContaining(self, container, msg=None):
    """Test that a container contains each of its elements."""
    for elem in container:
        self.assertIn(elem, container, msg)
