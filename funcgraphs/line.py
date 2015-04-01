# Copyright (C) 2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.

"""Module for representing, moving, shifting, stretching plotting and otherwise
manipulating line segments in a convenient fashion."""

import unittest

import numpy as np

from .coordinates import Point, Coordinates

__all__ = ["Line", "parabola"]


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


class Line(object):
    """ Line segment between two points. May be directed or undirected.
    Internally represented as an ordered tuple of points in the complex plane,
    (z1, z2); z1 is the tail, z2 is the head. This format is more convenient
    for many purposes. """

    def __init__(self, p1, p2):
        """input may be two complex numbers, or tuples (x1, y1), (x2, y2). """
        self.p1 = Point(p1)
        self.p2 = Point(p2)

    def __repr__(self):
        return type(self).__name__+'(p1=%s, p2=%s)' % (
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

    @property
    def coordinates(self):
        return Coordinates([self.p1, self.p2])

    def bisecting_line(self):
        """Return a perpendicular line segment with overlapping midpoint"""
        lc = self.coordinates
        lc.rotate(angle=np.pi/2, origin=self.midpoint)
        return self.__class__(lc[0], lc[1])

    def projection(self, p):
        """Return projection of point p onto the extended segment"""
        if self.length == 0:  # p1 == p2 case
            return self.p1
        # Consider the line extending the segment, parameterized as v+t*(w-v).
        # We find projection of point p onto the line.
        # It falls where t = [(p-v) . (w-v)] / |w-v|^2
        t = -(self.p1 - p)*(self.vector)/self.length**2
        if t < 0:
            return self.p1  # Beyond the 'p1' end of the segment
        elif t > 1:
            return self.p2  # Beyond the 'p2' end of the segment
        return self.p1 + t*(self.vector)

    def shorten(self, r):
        """Shorten the line segment by r/2 on each side."""
        self.p1 = self.p1 + Point.from_polar(r/2., self.vector.theta)
        self.p2 = self.p2 + Point.from_polar(r/2., self.vector.theta - np.pi)

    def draw_line(self, ax=None):
        """Draw the line segment on the current axis."""
        self.coordinates.plot(ax=None, color='blue', zorder=1)

    def connecting_parabola(self, d=1./3):
        """ Return a parabola sampled at n grid points connecting the end
        points of the line segment with peak distance r away from the
        connecting line. """
        r, theta = self.vector.r, self.vector.theta
        parab = parabola(r, d*self.length/2., n=100)
        parab.rotate(theta)
        return parab + self.p1

    def draw_parabola(self, d=1./3, ax=None):
        """Draw parabola of width d connecting the ends of the line segment"""
        self.connecting_parabola(d).plot(ax)
