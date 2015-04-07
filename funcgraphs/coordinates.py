# Copyright (C) 2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.

"""Module for representing and manipulating 2D cartesian coordinates both in
isolation and in groups."""

import numbers

import numpy as np
import matplotlib.pyplot as plt

__all__ = ["Point", "Coordinates"]


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
        return -(-self + other)

    def __rmul__(self, other):
        """Scale self by real value other. """
        if isinstance(other, numbers.Real):
            return self.__class__(other*self.z)
        raise TypeError("Cannot multiply coordinates by %s" % type(other))

    def __div__(self, other):
        """inverse of mul"""
        return (1./other) * self

    __truediv__ = __div__

    def rotate(self, angle, origin=0):
        """Rotate the locations by angle about point p, default is origin"""
        coords = self - origin
        r, theta = coords.r, coords.theta
        self._coord = (self.from_polar(r, theta + angle) + origin).z


def check_components_are_real(x, y):
    """Check that both x and y are real numbers, if not raise error"""
    isreal = lambda ob: isinstance(ob, numbers.Real)
    if not(isreal(x) and isreal(y)):
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
            check_components_are_real(x, y)
            z = x + 1j*y
        elif hasattr(x, '__iter__'):
            check_components_are_real(x[0], x[1])
            if len(x) != 2:
                raise ValueError("More than one coordinate specified.")
            z = x[0] + 1j*x[1]
        else:
            z = complex(x)  # Explicitly cast to complex (e.g. if ints)
        self._coord = z

    def __mul__(self, other):
        """Dot product with other vector."""
        other = Point(other)
        return self.x * other.x + self.y * other.y

    def __repr__(self):
        return self.__class__.__name__+'(%s, %s)' % (self.x, self.y)

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.z == other.z
        return False

    def __ne__(self, other):
        return not self == other

    def __complex__(self):
        return self.z


def check_coords_are_real(x, y):
    """Check that x and y are real valued arrays"""
    array_is_real = lambda arr: issubclass(arr.dtype.type, numbers.Real)
    if not(array_is_real(x) and array_is_real(y)):
        raise TypeError(
            ("Both coordinates must be real valued, received"
             " %s, %s" % (x.dtype.type.__name__, y.dtype.type.__name__))
        )


class Coordinates(LocationSpecifier2D):
    """A set of points internally represented by a numpy array."""

    def __init__(self, x, y=None):
        """All of the following inputs to point are equivalent:
            Coordinates([Point(1, 2), Point(3, 4), Point(5, 6)])
            Coordinates([1, 3, 5], [2, 4, 6])
            Coordinates([1+2j, 3+4j, 5+6j])
        Any other input will raise a value error."""
        x = np.array(x)
        if x.ndim != 1:
            raise TypeError("Input must be flat iterable location collection")
        if y is not None:
            y = np.array(y)
            check_coords_are_real(x, y)
            if x.shape != y.shape:
                raise ValueError("Inputs must be equal length")
            z = x + 1j*y
        else:
            z = x.astype(complex)
        self._coord = z

    def __repr__(self):
        return self.__class__.__name__+'(%s)' % list(self)

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

    def plot(self, *args, **kwargs):
        """Draw connected sequence of points"""
        if kwargs.get('ax', None) is not None:
            ax = kwargs['ax']
        else:
            ax = plt.gca()
        kwargs.pop('ax', None)
        ax.plot(self.x, self.y, *args, **kwargs)
