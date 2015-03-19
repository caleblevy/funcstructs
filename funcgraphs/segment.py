# Copyright (C) 2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.

""" Module for representing, moving, shifting, stretching plotting and
otherwise manipulating line segments in a convenient fashion. """

import numbers
import unittest

import numpy as np
import matplotlib.pyplot as plt


class LocationSpecifier2D(object):
    """Abstract coordinates. Invoked either as a point or a point cloud. """

    def __init__(self, x, y=None):
        # Conceptually, Location2D should be an abstract base class. However,
        # without some ugly hacks or third party libraries, there is no python
        # 2 and 3 compatible syntax for specifying a metaclass, so we mock
        # ABCMeta by raising an error at instantiation.
        raise NotImplementedError("Cannot call LocationSpecifier2D directly.")

    @classmethod
    def from_polar(cls, r, theta):
        return cls(r*np.exp(1j*theta))

    @property
    def z(self):
        """Return the locations as points on the complex plane"""
        return self._coord

    def __abs__(self):
        return np.abs(self.z)

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
        return abs(self)

    @property
    def theta(self):
        """Return the angular component of the polar representation"""
        return np.arctan2(self.y, self.x)

    def __add__(self, other):
        """Change to coordinates in which old origin is now at other in new"""
        return self.__class__(self.z + Point(other).z)

    def __neg__(self):
        """Reflection about the origin"""
        return self.__class__(-self.z)

    def __sub__(self, other):
        """Change to coordinates such that new origin is at other in the old"""
        return self + (-other)

    def __rmul__(self, other):
        """Scale self by real value other. """
        if not hasattr(other, '__iter__') and other == other.real:
            return self.__class__(other*self.z)
        raise TypeError("Cannot multiply coordinates by %s" % str(type(other)))

    def __div__(self, other):
        """inverse of mul"""
        return (1./other) * self

    __truediv__ = __div__

    def rotate(self, angle, origin=0):
        """Rotate the locations by angle about point p, default is origin"""
        p = Point(origin)
        coords = self - p
        r, theta = coords.r, coords.theta
        self._coord = (self.from_polar(r, theta - angle) + p).z


def check_coords_are_real(x, y):
    """Check that both x and y are real numbers, if not raise error"""
    if not all(map(lambda x: isinstance(x, numbers.Real), [x, y])):
        raise TypeError(
            ("Both coordinates must be real numbers, "
             "received %s, %s") % (type(x).__name__, type(y).__name__)
        )


class Point(LocationSpecifier2D):
    """A basic cartesian point. Internally represented as a complex number
    (i.e. a point in the complex plane)."""

    def __init__(self, x, y=None):
        """All of the following inputs to point are equivalent:
            Point(1, 2)
            Point((1, 2))
            Point(1+2j)
            Point(Point(1, 2))
        Any other input will raise a value error."""
        if y is not None:
            check_coords_are_real(x, y)
            z = x + 1j*y
        elif hasattr(x, '__iter__'):
            if len(x) != 2:
                raise ValueError("More than one coordinate specified.")
            check_coords_are_real(x[0], x[1])
            z = x[0] + 1j*x[1]
        elif isinstance(x, numbers.Complex):
            z = x.real + 1j*x.imag  # Explicitly cast to complex (e.g. if ints)
        elif isinstance(x, self.__class__):
            z = x.z
        else:
            raise TypeError("Cannot parse coordinates from %s, %s" % (
                type(x).__name__,
                type(y).__name__
                )
            )
        self._coord = z

    def __mul__(self, other):
        """Dot product with other vector."""
        return self.x * Point(other).x + self.y * Point(other).y

    def __repr__(self):
        return self.__class__.__name__+'(%s, %s)' % (str(self.x), str(self.y))

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.z == other.z
        return False

    def __ne__(self, other):
        return not self == other


def coordinate_parser(x, y=None):
    """Parses tuples, complex numbers and pairs of inputs for Point and
    PointCloud classes."""
    if isinstance(x, LocationSpecifier2D):
        return x.z
    elif y is not None:
        return x + 1j*y
    else:
        return x.real + 1j*x.imag  # ensure coordinates are cast as complex


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

    def __getitem__(self, key):
        """Return the nth point in the cloud"""
        if isinstance(key, int):
            return Point(self.z[key])
        return Coordinates(self.z[key])


def parabola(sep, h, cut_short=0., n=100):
    """ Return the array of x + 1j*f(x) sampled at n evenly spaced points on
    the interval [cut_short, sep - cut_short], where f(x) is a parabola
    satisfying f(0)=f(sep)=0 and f(sep/2)=h.

    Used to construct curved arrows pointing between nodes of a graph. """
    k = sep/2.
    x_s = cut_short - k
    x_f = k - cut_short
    x = np.linspace(x_s, x_f, n)
    f = -h/(1.*k**2) * (x + k) * (x - k)
    z = x + 1j*f
    return Coordinates(z + k)


class LineSegment(object):
    """ Line segment between two points. May be directed or undirected.
    Internally represented as an ordered tuple of points in the complex plane,
    (z1, z2); z1 is the tail, z2 is the head. This format is more convenient
    for many purposes. """

    def __init__(self, p1, p2):
        """input may be two complex numbers, or tuples (x1, y1), (x2, y2). """
        self.p1 = Point(p1)
        self.p2 = Point(p2)

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

    @property
    def vector(self):
        """Displacement vector from beginning of segment to end"""
        return self.p2 - self.p1

    @property
    def length(self):
        return self.vector.r

    # Slope-intercept form: y = m*x + b

    @property
    def m(self):
        """Return the slope fo the line segment"""
        rise = self.p2.y - self.p1.y
        run = self.p2.x - self.p1.x
        if run:
            return 1.*rise/run
        if rise:
            return rise/abs(rise)*float('inf')
        raise ZeroDivisionError

    @property
    def b(self):
        """Return the y-intercept of the extended line segment"""
        return self.p1.y - self.m * self.p1.x

    @property
    def midpoint(self):
        return (self.p1 + self.p2)/2

    def bisecting_line(self):
        """Return a perpendicular line segment with overlapping midpoint"""
        lc = Coordinates(np.array([self.p1.z, self.p2.z]))
        lc.rotate(angle=np.pi/2, origin=self.midpoint)
        return self.__class__(lc[0], lc[1])

    def projection(self, p):
        """Return projection of point p onto the extended segment"""
        p = Point(p)
        m_perp = -1./self.m
        b_perp = p.y - m_perp*p.x
        x_int = 1.*(self.b - b_perp)/(m_perp - self.m)
        y_int = self.m*x_int + self.b
        return Point(x_int, y_int)

    def shorten(self, r):
        """Shorten the line segment by r/2 on each side."""
        self.p1 = self.p1 + Point.from_polar(r/2., self.vector.theta)
        self.p2 = self.p2 + Point.from_polar(r/2., self.vector.theta - np.pi)

    def draw_line(self, ax=None):
        """Draw the line segment on the current axis."""
        if ax is None:
            ax = plt.gca()
        x1, y1 = self.p1.x, self.p1.y
        x2, y2 = self.p2.x, self.p2.y
        x = np.array([x1, x2])
        y = np.array([y1, y2])
        ax.plot(x, y, color='black', zorder=1)

    def connecting_parabola(self, d, n=100):
        """ Return a parabola sampled at n grid points connecting the end
        points of the line segment with peak distance r away from the
        connecting line. """
        r, theta = self.vector.r, self.vector.theta
        parab = parabola(r, d, n=n)
        r_p, theta_p = parab.r, parab.theta
        return Coordinates.from_polar(r_p, theta_p + theta) + self.p1

    def draw_parabola(self, d=1./3, ax=None):
        """Draw parabola of width d connecting the ends of the line segment"""
        if ax is None:
            ax = plt.gca()
        parab = self.connecting_parabola(d*self.length/2)
        ax.plot(parab.x, parab.y)


class CoordinateTests(unittest.TestCase):

    def test_init(self):
        """Ensure equivalence of various ways to initialize a point."""
        p1 = Point(1, 2)
        p2 = Point(1 + 2j)
        p3 = Point((1, 2))
        self.assertAlmostEqual(p1, p2)
        self.assertAlmostEqual(p1, p3)
        self.assertAlmostEqual(p2, p3)
        self.assertAlmostEqual(p1, Point(p1))

    def test_repr(self):
        p1 = Point(1., 2.)
        p2 = Point(-7, 56)
        self.assertAlmostEqual(p1, eval(repr(p1)))
        self.assertAlmostEqual(p2, eval(repr(p2)))

    def test_polar(self):
        """Test forming a vector from polar coordinates behaves correctly."""
        # Test the origin
        o = Point(0, 0)
        p = Point.from_polar(0, 0)
        self.assertAlmostEqual(p, o)
        # Test a vertical line
        h = Point.from_polar(2, np.pi/2)
        self.assertAlmostEqual(Point(0, 2), h)
        # Test periodic in 2*pi
        k1 = Point.from_polar(2, -3)
        k2 = Point.from_polar(2, -3+2*np.pi)
        self.assertAlmostEqual(k1, k2)

    def test_coordinate_transforms(self):
        """Test going back and forth from cartesian to polar."""
        # From polar to cartesian
        p1 = Point(1, 2)
        rp1 = Point.from_polar(p1.r, p1.theta)
        self.assertAlmostEqual(p1, rp1)
        # From Cartesian to polar
        p2 = Point(-1, 1)
        self.assertAlmostEqual(np.sqrt(2), p2.r)
        self.assertAlmostEqual(3*np.pi/4, p2.theta)

    def test_negation(self):
        """Test that negation mirrors points about y=-x"""
        self.assertAlmostEqual(Point(-1, -2), -Point(1, 2))

    def test_coordinates(self):
        """Test arrays of coordinates"""
        coords = Coordinates(np.arange(10), np.arange(10)**2)
        for i, p in enumerate(coords):
            self.assertAlmostEqual(Point(i, i**2), p)
            self.assertAlmostEqual(p, coords[i])
        self.assertEqual(10, len(coords))
        np.testing.assert_array_almost_equal(
            coords.z,
            Coordinates.from_polar(coords.r, coords.theta).z
        )

    def test_dot_product(self):
        """Test values for the dot product of points"""
        p1 = Point((1, 2))
        p2 = Point((3, 4))
        # Test commutativity
        self.assertEqual(11, p1 * p2)
        self.assertEqual(11, p2 * p1)
        p3 = Point(-2, 1)
        self.assertEqual(0., p1 * p3)
        self.assertEqual(0., p3 * p1)

    def test_rotation(self):
        """Test rotation and unrotation of a point"""
        # Test rotation maintains object identity
        a = Point(1, 2)
        ai = id(a)
        a.rotate(3)
        a.rotate(-3)
        self.assertEqual(ai, id(a))
        self.assertAlmostEqual(Point(1, 2), a)
        a.rotate(np.pi)
        self.assertAlmostEqual(-Point(1, 2), a)
        # Test dot product with perpendicular is zero
        b = Point(3, -4)
        br = Point(b)
        br.rotate(np.pi/2)
        self.assertAlmostEqual(0, b * br)


class LineTests(unittest.TestCase):

    def assertLinesEqual(self, l1, l2):
        """Test two line segments contain the same points."""
        lsort = lambda l: sorted([(l.p1.x, l.p1.y), (l.p2.x, l.p2.y)])
        l1_points = lsort(l1)
        l2_points = lsort(l2)
        for p, q in zip(l1_points, l2_points):
            self.assertAlmostEqual(Point(p), Point(q))

    def test_length(self):
        """Verify the length of a 3-4-5 isosceles right triangle."""
        pythag = LineSegment(0, (3, 4))
        self.assertAlmostEqual(5, pythag.length)

    def test_slope(self):
        """Test slopes of the lines"""
        l1 = LineSegment(1+2j, 3+7j)
        l2 = LineSegment((1, 2), (3, 7))
        self.assertAlmostEqual(2.5, l1.m)
        self.assertAlmostEqual(l1.m, l2.m)
        # Test vertical line gives infinite slope
        l_vert = LineSegment(0, 1j)
        self.assertEqual(float('inf'), l_vert.m)
        # Test zero length line raises error
        with self.assertRaises(ZeroDivisionError):
            LineSegment((1, 1), (1, 1)).m

    def test_vector(self):
        """Test angle of unit vector is tangent of the slope."""
        l1 = LineSegment((1, 3), (1, 7))
        l2 = LineSegment(0, (-1, -1))
        self.assertAlmostEqual(np.pi/2., l1.vector.theta)
        self.assertAlmostEqual(np.sqrt(2), l2.vector.r)

    def test_repr(self):
        l = LineSegment((1, 2), (3, 7))
        self.assertEqual(l, eval(repr(l)))

    def test_projection(self):
        """Test projection on the line y = x"""
        l = LineSegment((-1, -1), (1, 1))
        self.assertEqual(Point(0, 0), l.projection((-1, 1)))
        self.assertEqual(Point(0, 0), l.projection((2, -2)))
        self.assertEqual(Point(5.5, 5.5), l.projection((7, 4)))

    def test_bisecting_line(self):
        """Test bisection is same length, perpendicular and shares midpoints"""
        l = LineSegment((3, 7), (4, 2))
        lp = l.bisecting_line()
        lpp = lp.bisecting_line()
        self.assertLinesEqual(l, lpp)
        self.assertAlmostEqual(-1./l.m, lp.m)
        self.assertAlmostEqual(l.length, lp.length)
        self.assertAlmostEqual(l.midpoint, lp.midpoint)

    def test_shorten(self):
        """Test shortening clips the line segments"""
        a = LineSegment((1, 2), (5, 4))
        b = LineSegment((1, 2), (5, 4))
        a.shorten(0.5)
        self.assertAlmostEqual(b.length - 0.5, a.length)


if __name__ == '__main__':
    unittest.main()
