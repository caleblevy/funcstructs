# Copyright (C) 2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.

""" Module for representing, moving, shifting, stretching plotting and
otherwise manipulating line segments in a convenient fashion. """

import unittest

import numpy as np


class Coordinates(object):
    """Abstract coordinates. Invoked either as a point or a point cloud. """

    def __init__(self, x, y=None):
        """ Takes either a single complex number z, a tuple (x, y) or real and
        imaginary part separately. I.E. Point(0, 1) == Point(0+1j) ==
        Point((1,2)) == Point(Point(0, 1)). """

        if isinstance(x, self.__class__):
            self._coord = x._coord
        elif y is not None:
            self._coord = x + 1j*y
        else:
            self._coord = x.real + 1j*x.imag

    @classmethod
    def from_polar(cls, r, theta):
        return cls(r*np.exp(1j*theta))

    @property
    def z(self):
        return self._coord

    @property
    def x(self):
        return self.z.real

    @property
    def y(self):
        return self.z.imag

    @property
    def r(self):
        return np.abs(self.z)

    @property
    def theta(self):
        return np.arctan2(self.y, self.x)

    def __repr__(self):
        return self.__class__.__name__+'(%s, %s)' % (str(self.x), str(self.y))

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self._coord == other._coord
        return False

    def __ne__(self, other):
        return not self == other

    def __add__(self, other):
        return self.__class__(self.z + Point(other).z)

    def __neg__(self):
        return self.__class__(-self.z)

    def __sub__(self, other):
        return self + (-other)

    def __rmul__(self, other):
        """Scale self by real value other. """
        if other == other.real:
            return self.__class__(other*self.z)
        raise TypeError("Cannot multiply coordinates by %s" % str(type(other)))

    def __div__(self, other):
        return (1./other) * self


class Point(Coordinates):
    """ A basic cartesian point. Internally represented as a complex number
    (i.e. a point in the complex plane). """

    def __init__(self, x, y=None):
        if hasattr(x, '__iter__'):
            if not(len(x) == 2 and y is None):
                raise TypeError("More than one coordinate specified.")
            x, y = x[0], x[1]
        super(Point, self).__init__(x, y)


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
        rise = self.p1.y - self.p2.y
        run = 1.*(self.p1.x - self.p2.x)
        try:
            m = rise/run
        except ZeroDivisionError as e:
            if abs(rise) > 0:
                m = float('Inf')
            else:
                raise e
        return m

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
        self.assertEqual(p1, p2)
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

    def test_points_are_not_coordinates(self):
        self.assertFalse(Point(1, 2) == Coordinates(1, 2))
        self.assertFalse(Coordinates(1, 2) == Point(1, 2))
        self.assertTrue(Coordinates(1, 2) == Coordinates(1, 2))
        self.assertTrue(Point(1, 2) == Point(1, 2))


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
