# Copyright (C) 2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.

""" Module for representing, moving, shifting, stretching plotting and
otherwise manipulating line segments in a convenient fashion. """

import unittest

import numpy as np


class Point(object):
    """ A basic cartesian point. Internally represented as a complex number
    (i.e. a point in the complex plane). """

    def __init__(self, x, y=None):
        """ Takes either a single complex number z, a tuple (x, y) or real and
        imaginary part separately. I.E. Point(0, 1) == Point(0+1j) =
        Point(Point(0, 1)). """
        if isinstance(x, self.__class__):
            self._coord = x._coord
        elif y is not None:
            self._coord = x + 1j*y
        else:
            self._coord = x.real + 1j*x.imag

    @classmethod
    def from_polar(cls, r, theta=None):
        if hasattr(r, '__iter__'):
            r, theta = r
        return cls(r*np.exp(1j*theta))

    @property
    def x(self):
        return self._coord.real

    @property
    def y(self):
        return self._coord.imag

    @property
    def r(self):
        return abs(self._coord)

    @property
    def theta(self):
        return np.arctan2(self.y, self.x)

    @property
    def z(self):
        return self._coord

    def __repr__(self):
        return self.__class__.__name__+'(%s, %s)'%(str(self.x), str(self.y))

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self._coord == other._coord
        return False

    def __ne__(self, other):
        return not self == other

    def __add__(self, other):
        return self.__class__(self._coord + other._coord)

    def __neg__(self):
        return self.__class__(-self._coord)

    def __sub__(self, other):
        return self + (-other)


class LineSegment(object):
    """ Line segment between two points. May be directed or undirected.
    Internally represented as an ordered tuple of points in the complex plane,
    (z1, z2); z1 is the tail, z2 is the head. This format is more convenient
    for many purposes. """

    def __init__(self, p1, p2, arrow=False):
        """input may be two complex numbers, or tuples (x1, y1), (x2, y2). """
        self.p1 = Point(z1)
        self.p2 = Point(z2)
        self._is_arrow = arrow

    def vector(self):
        return self.p2 - self.p1

    @property
    def length(self):
        return abs(self.vector())

    def unit(self):
        return self.vector()/(1.*self.length)

    @property
    def slope(self):
        return (p1.y - p2.y)/(1.*(p1.x - p2.x))


class PointTests(unittest.TestCase):

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

if __name__ == '__main__':
    unittest.main()