import unittest

import numpy as np

from ..coordinates import *


class Location2DTests(unittest.TestCase):

    def test_polar_coordinates(self):
        """Test going back and forth from cartesian to polar."""
        # From polar to cartesian
        p1 = Point(1, 2)
        rp1 = Point.from_polar(p1.r, p1.theta)
        self.assertAlmostEqual(p1, rp1)
        # From Cartesian to polar
        p2 = Point(-1, 1)
        self.assertAlmostEqual(np.sqrt(2), p2.r)
        self.assertAlmostEqual(3*np.pi/4, p2.theta)
        # Test on arrays
        x = np.linspace(0, 1, 10)
        c = Coordinates(x, x)
        for p in c[1:]:
            self.assertAlmostEqual(np.pi/4, p.theta)

    def test_from_polar(self):
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
        # test coordinate array
        x = np.linspace(0, 1, 10)
        par = Coordinates(x, x**2)
        np.testing.assert_allclose(
            par.z,
            Coordinates.from_polar(par.r, par.theta).z
        )
        self.assertAlmostEqual(par.theta[-1], np.pi/4)

    def test_negation(self):
        """Test that negation mirrors points about y=-x"""
        self.assertAlmostEqual(Point(-1, -2), -Point(1, 2))
        # test on arrays
        np.testing.assert_allclose(
            Coordinates([Point(-1, -2), Point(3, -4), Point(4, -5)]).z,
            -Coordinates([Point(1, 2), Point(-3, 4), Point(-4, 5)]).z
        )

    def test_rotation(self):
        """Test rotation and unrotation of a point"""
        # Test rotation maintains object identity
        a = Point(1, 2)
        ai = a
        a.rotate(3)
        a.rotate(-3)
        self.assertIs(ai, a)
        self.assertAlmostEqual(Point(1, 2), a)
        a.rotate(np.pi)
        self.assertAlmostEqual(-Point(1, 2), a)
        # Test dot product with perpendicular is zero
        b = Point(3, -4)
        br = Point(b)
        br.rotate(np.pi/2)
        self.assertAlmostEqual(0, b * br)
        # Test rotating coordinates
        x = np.linspace(0, 1, 10)
        par = Coordinates(x, x**2)
        par.rotate(np.pi/4)
        self.assertAlmostEqual(np.pi/2, par[-1].theta)


class PointTests(unittest.TestCase):

    def test_init(self):
        """Ensure equivalence of various ways to initialize a point."""
        points = [Point(1, 2), Point((1, 2)), Point(1+2j), Point(Point(1, 2))]
        for p in points:
            for q in points:
                self.assertAlmostEqual(p, q)
        erroneous_args = [
            {'x': 1, 'y': 2j},  # y is complex
            {'x': 1j, 'y': 2},  # x is complex with sepcified y
            {'x': [1], 'y': [2]},  # x and y both lists
            {'x': [1]},  # Not enough coordinates
            {'x': [1, 2, 3]},  # Too many coordinates
            {'x': [1, 2j]},  # Complex values in coordinate tuple
            {'x': Point(1, 2), 'y': Point(3, 4)},  # Two complex valued points
            {'x': np.array(1)}  # 0-dim array
        ]
        for components in erroneous_args:
            with self.assertRaises(Exception):
                Point(**components)

    def test_repr(self):
        p1 = Point(1., 2.)
        p2 = Point(-7, 56)
        self.assertAlmostEqual(p1, eval(repr(p1)))
        self.assertAlmostEqual(p2, eval(repr(p2)))

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


class CoordinateTests(unittest.TestCase):

    def test_init(self):
        coord_sets = [
            Coordinates([Point(1, 2), Point(3, 4), Point(5, 6)]),  # point list
            Coordinates([1, 3, 5], [2, 4, 6]),  # from x and y components
            Coordinates([1+2j, 3+4j, 5+6j])  # from locations on complex pane
        ]
        for c in coord_sets:
            for d in coord_sets:
                np.testing.assert_allclose(c.z, d.z)
        erroneous_args = [
            {'x': [1, 2, Point(1)], 'y': [1, 2, 3]},  # complex x component
            {'x': [1, 2, 1], 'y': [1, 2, 3j]},  # complex y component
            {'x': [1, 3, 5], 'y': [1, 2j]},  # more x components than y
            {'x': [1, 2], 'y': [1, 2, 3]},  # more y components
            {'x': [1, 2, [3]]},  # iterable points
            {'x': 1, 'y': 2},  # uniterable coordinates
            {'x': [(1, 2), (3, 4), (5, 6)]},  # tuple components
        ]
        for components in erroneous_args:
            with self.assertRaises(Exception):
                Coordinates(**components)

    def test_repr(self):
        coords1 = Coordinates([1, 2, 3], [4, 5, 6])
        coords2 = Coordinates(range(10), np.arange(10)**2)
        np.testing.assert_allclose(coords1.z, eval(repr(coords1)).z)
        np.testing.assert_allclose(coords2.z, eval(repr(coords2)).z)

    def test_container_methods(self):
        """Test __iter__, __len__ and __getitem__ methods"""
        coords = Coordinates(range(10), np.arange(10)**2)
        for i, p in enumerate(coords):
            self.assertAlmostEqual(Point(i, i**2), p)
            self.assertAlmostEqual(p, coords[i])
        self.assertEqual(10, len(coords))
        np.testing.assert_allclose(
            coords.z,
            Coordinates.from_polar(coords.r, coords.theta).z
        )
