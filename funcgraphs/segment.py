# Copyright (C) 2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.

""" Module for representing, moving, shifting, stretching plotting and
otherwise manipulating line segments in a convenient fashion. """

import unittest

import numpy as np


class LocationSpecifier2D(object):
    """Abstract coordinates. Invoked either as a point or a point cloud. """

    def __init__(self, x, y=None):
        # Conceptually, Location2D should be an abstract base class. However,
        # without some ugly hacks or third party libraries, there is no python
        # 2 and 3 compatible syntax for specifying a metaclass, so we mock
        # ABCMeta by raising an error at instantiation.
        raise NotImplementedError("Cannot call coordinates directly.")

    @classmethod
    def from_polar(cls, r, theta):
        return cls(r*np.exp(1j*theta))

    @property
    def z(self):
        """Return the locations as points on the complex plane"""
        return self._coord

    @property
    def x(self):
        """Return x components of the cartesian representations"""
        return self.z.real

    @property
    def y(self):
        """Return the y components of cartesian representations"""
        return self.z.imag

    @property
    def r(self):
        """Return radial components of the polar representation"""
        return np.abs(self.z)

    @property
    def theta(self):
        """Return the angular component of the polar representation"""
        return np.arctan2(self.y, self.x)

    def __add__(self, other):
        """Reverse of __sub__"""
        return self.__class__(self.z + Point(other).z)

    def __neg__(self):
        """Reflection about the origin"""
        return self.__class__(-self.z)

    def __sub__(self, other):
        """Representation with origin shifted to other."""
        return self + (-other)

    def __rmul__(self, other):
        """Scale self by real value other. """
        if other == other.real:
            return self.__class__(other*self.z)
        raise TypeError("Cannot multiply coordinates by %s" % str(type(other)))

    def __div__(self, other):
        """inverse of mul"""
        return (1./other) * self


def coordinate_parser(x, y=None):
    """Parses tuples, complex numbers and pairs of inputs for Point and
    PointCloud classes."""
    if isinstance(x, LocationSpecifier2D):
        return x.z
    elif y is not None:
        return x + 1j*y
    else:
        return x.real + 1j*x.imag  # ensure coordinates are cast as complex


class Point(LocationSpecifier2D):
    """A basic cartesian point. Internally represented as a complex number
    (i.e. a point in the complex plane)."""

    def __init__(self, x, y=None):
        """Takes either a single complex number z, a tuple (x, y) or real and
        imaginary part separately. i.e. Point(0, 1) == Point(0+1j) == Point((1,
        2)) == Point(Point(0, 1))."""
        if hasattr(x, '__iter__'):
            if not(len(x) == 2 and y is None):
                raise TypeError("More than one coordinate specified.")
            x, y = x[0], x[1]
        self._coord = coordinate_parser(x, y)

    def __repr__(self):
        return self.__class__.__name__+'(%s, %s)' % (str(self.x), str(self.y))

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.z == other.z
        return False

    def __ne__(self, other):
        return not self == other


class Coordinates(LocationSpecifier2D):
    """A set of points."""

    def __init__(self, x, y=None):
        """ Takes either two equal length arrays of real numbers or one array
        of complex numbers. """
        z = coordinate_parser(x, y)
        if isinstance(z, complex):
            z = np.array([z])
        self._coord = z

    def __len__(self):
        """Number of points in the set"""
        return len(self.z)

    def __iter__(self):
        """Enumerate all points in z."""
        for p in self.z:
            yield Point(p)


class LineSegment(object):
    """ Line segment between two points. May be directed or undirected.
    Internally represented as an ordered tuple of points in the complex plane,
    (z1, z2); z1 is the tail, z2 is the head. This format is more convenient
    for many purposes. """

    def __init__(self, p1, p2):
        """input may be two complex numbers, or tuples (x1, y1), (x2, y2). """
        self.p1 = Point(p1)
        self.p2 = Point(p2)

    @property
    def vector(self):
        return self.p2 - self.p1

    @property
    def length(self):
        return self.vector.r

    @property
    def unit(self):
        return self.vector/(1.*self.length)

    @property
    def slope(self):
        rise = self.p2.y - self.p1.y
        run = 1.*(self.p2.x - self.p1.x)
        if run:
            return rise/run
        if rise:
            return rise/abs(rise)*float('inf')
        raise ZeroDivisionError

    @property
    def midpoint(self):
        return (self.p1 + self.p2)/2.

    def __add__(self, other):
        return self.__class__(self.p1 + Point(other), self.p2 + Point(other))

    def __repr__(self):
        return self.__class__.__name__+'(p1=%s, p2=%s)' % (
            str(self.p1),
            str(self.p2)
        )

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.p1 == other.p1 and self.p2 == other.p2
        return False

    def __ne__(self, other):
        return not self == other


class CoordinateTests(unittest.TestCase):

    def test_init(self):
        """Ensure equivalence of various ways to initialize a point."""
        p1 = Point(1, 2)
        p2 = Point(1 + 2j)
        p3 = Point((1, 2))
        self.assertEqual(p1, p2)
        self.assertEqual(p1, p3)
        self.assertEqual(p2, p3)
        self.assertEqual(p1, Point(p1))

    def test_repr(self):
        p1 = Point(1., 2.)
        self.assertTrue(p1 == eval(repr(p1)))
        p2 = Point(-7, 56)
        self.assertTrue(p2 == eval(repr(p2)))

    def test_polar(self):
        """Test forming a vector from polar coordinates behaves correctly."""
        # Test the origin
        o = Point(0, 0)
        p = Point.from_polar(0, 0)
        self.assertEqual(p, o)
        # Test a vertical line
        h = Point.from_polar(2, np.pi/2)
        self.assertAlmostEqual(h.x, 0)
        self.assertAlmostEqual(h.y, 2)
        # Test periodic in 2*pi
        k1 = Point.from_polar(2, -3)
        k2 = Point.from_polar(2, -3+2*np.pi)
        self.assertAlmostEqual(k1.x, k2.x)
        self.assertAlmostEqual(k1.y, k2.y)

    def test_coordinate_transforms(self):
        """Test going back and forth from cartesian to polar."""
        # From polar to cartesian
        p1 = Point(1, 2)
        rp1 = Point.from_polar(p1.r, p1.theta)
        self.assertAlmostEqual(0, (p1-rp1).x)
        self.assertAlmostEqual(0, (p1-rp1).y)
        # From Cartesian to polar
        p2 = Point(-1, 1)
        self.assertAlmostEqual(np.sqrt(2), p2.r)
        self.assertAlmostEqual(3*np.pi/4, p2.theta)

    def test_negation(self):
        """Test that negation mirrors points about y=-x"""
        p1 = -Point(1, 2)
        self.assertAlmostEqual(-1, p1.x)
        self.assertAlmostEqual(-2, p1.y)

    def test_coordinates(self):
        """Test arrays of coordinates"""
        coords = Coordinates(np.arange(10), np.arange(10)**2)
        for i, p in enumerate(coords):
            self.assertAlmostEqual(i, p.x)
            self.assertAlmostEqual(i**2, p.y)
        self.assertEqual(10, len(coords))
        np.testing.assert_array_almost_equal(
            coords.z,
            Coordinates.from_polar(coords.r, coords.theta).z
        )


class LineTests(unittest.TestCase):

    def test_length(self):
        """Verify the length of a 3-4-5 isosceles right triangle."""
        pythag = LineSegment(0, (3, 4))
        self.assertAlmostEqual(5, pythag.length)

    def test_slope(self):
        """Test slopes of the lines"""
        l1 = LineSegment(1+2j, 3+7j)
        l2 = LineSegment((1, 2), (3, 7))
        self.assertAlmostEqual(2.5, l1.slope)
        self.assertAlmostEqual(l1.slope, l2.slope)
        # Test vertical line gives infinite slope
        l_vert = LineSegment(0, 1j)
        self.assertEqual(float('inf'), l_vert.slope)
        # Test zero length line raises error
        with self.assertRaises(ZeroDivisionError):
            LineSegment((1, 1), (1, 1)).slope

    def test_unit(self):
        """Test angle of unit vector is tangent of the slope."""
        l1 = LineSegment((1, 3), (1, 7))
        l2 = LineSegment(0, (-1, -1))
        self.assertAlmostEqual(np.pi/2., l1.unit.theta)

    def test_repr(self):
        l = LineSegment((1, 2), (3, 7))
        self.assertEqual(l, eval(repr(l)))

if __name__ == '__main__':
    unittest.main()
