"""TestCase with stronger assertions."""

import pickle
from itertools import combinations, combinations_with_replacement
from unittest import TestCase


class StrongTestCase(TestCase):
    """A test case with stronger assertions than unittest.TestCase."""

    def assertIsTrue(self, expr, msg=None):
        """Assert than an expression evaluates identically to 'True'."""
        self.assertIs(True, expr, msg)

    def assertIsFalse(self, expr, msg=None):
        """Assert that an expression evaluates identically to 'False'."""
        self.assertIs(False, expr, msg)

    def assertFullyEqual(self, first, second, check_type=False, msg=None):
        """Enhanced version of the assertEqual method for checking custom
        equality operations. Tests both that a == b and b == a, and
        that a != b and b != a evaluate 'False'.
        """
        self.assertIsTrue(first == second, msg)
        self.assertIsTrue(second == first, msg)
        self.assertIsFalse(first != second, msg)
        self.assertIsFalse(second != first, msg)
        if check_type:
            self.assertIs(first.__class__, second.__class__, msg)

    def assertFullyUnequal(self, first, second, check_type=False, msg=None):
        """Enhanced version of the assertNotEqual method for checking custom
        equality operations. Tests both that a != b and b != a, and that
        a == b and b == a evaluate 'False'.
        """
        if check_type and(first.__class__ is not second.__class__):
            return
        self.assertIsFalse(first == second, msg)
        self.assertIsFalse(second == first, msg)
        self.assertIsTrue(first != second, msg)
        self.assertIsTrue(second != first, msg)

    def assertAllEqual(self, *objects, **kwargs):
        """Assert all the objects are fully equal."""
        for obj1, obj2 in combinations_with_replacement(objects, 2):
            self.assertFullyEqual(obj1, obj2, **kwargs)

    def assertAllUnique(self, *objects, **kwargs):
        """Assert that all of the given objects are unique."""
        for obj1, obj2 in combinations(objects, 2):
            self.assertFullyUnequal(obj1, obj2, **kwargs)

    def assertReprEvaluatesEqual(self, obj, msg=None):
        # assertReprEvaluatesEqual(self, obj, locals=locals, globals=globals)
        #   if callable(locals):
        #       locals = locals()
        #   if callable(globals):
        #       globals = globals
        """Test repr(obj) is a valid expression returning obj."""
        r = eval(repr(obj))
        self.assertFullyEqual(obj, r, msg)
        self.assertIs(obj.__class__, r.__class__, msg)

    def assertPicklable(self, obj, msg=None):
        """Test that obj is serializable and its pickle evaluates to itself."""
        p = pickle.loads(pickle.dumps(obj))
        self.assertFullyEqual(obj, p, msg)
        self.assertIs(obj.__class__, p.__class__, msg)

    def assertSerializable(self, obj, msg=None):
        """Test that obj can be round-tripped both by pickling and repr-eval"""
        self.assertReprEvaluatesEqual(obj, msg)
        self.assertPicklable(obj, msg)

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
