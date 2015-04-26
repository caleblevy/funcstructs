import unittest

import numpy as np

from ..coordinates import Point
from ..line import *


def lsort(l): return sorted([(l.p1.x, l.p1.y), (l.p2.x, l.p2.y)])


class LineTests(unittest.TestCase):

    def assertLinesEqual(self, l1, l2):
        """Test two line segments contain the same points."""
        l1_points = lsort(l1)
        l2_points = lsort(l2)
        for p, q in zip(l1_points, l2_points):
            self.assertAlmostEqual(Point(p), Point(q))

    def test_length(self):
        """Verify the length of a 3-4-5 isosceles right triangle."""
        pythag = Line(0, (3, 4))
        self.assertAlmostEqual(5, pythag.length)

    def test_slope(self):
        """Test slopes of the lines"""
        l1 = Line(1+2j, 3+7j)
        l2 = Line((1, 2), (3, 7))
        self.assertAlmostEqual(2.5, l1.m)
        self.assertAlmostEqual(l1.m, l2.m)
        # Test vertical line gives infinite slope
        l_vert = Line(0, 1j)
        self.assertEqual(float('inf'), l_vert.m)
        # Test zero length line raises error
        with self.assertRaises(ZeroDivisionError):
            Line((1, 1), (1, 1)).m

    def test_vector(self):
        """Test angle of unit vector is tangent of the slope."""
        l1 = Line((1, 3), (1, 7))
        l2 = Line(0, (-1, -1))
        self.assertAlmostEqual(np.pi/2., l1.vector.theta)
        self.assertAlmostEqual(np.sqrt(2), l2.vector.r)

    def test_repr(self):
        l = Line((1, 2), (3, 7))
        self.assertEqual(l, eval(repr(l)))

    def test_projection(self):
        """Test projection on the line y = x"""
        l = Line((-1, -1), (1, 1))
        self.assertAlmostEqual(Point(0, 0), l.projection((-1, 1)))
        self.assertAlmostEqual(Point(0, 0), l.projection((2, -2)))
        self.assertAlmostEqual(Point(1, 1), l.projection((7, 4)))
        self.assertAlmostEqual(Point(1./2, 1./2), l.projection((0, 1)))

    def test_bisecting_line(self):
        """Test bisection is same length, perpendicular and shares midpoints"""
        l = Line((3, 7), (4, 2))
        lp = l.bisecting_line()
        lpp = lp.bisecting_line()
        self.assertLinesEqual(l, lpp)
        self.assertAlmostEqual(-1./l.m, lp.m)
        self.assertAlmostEqual(l.length, lp.length)
        self.assertAlmostEqual(l.midpoint, lp.midpoint)

    def test_shorten(self):
        """Test shortening clips the line segments"""
        a = Line((1, 2), (5, 4))
        b = Line((1, 2), (5, 4))
        a.shorten(0.5)
        self.assertAlmostEqual(b.length - 0.5, a.length)
