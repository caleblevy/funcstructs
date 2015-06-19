"""Module for representing and manipulating 2D cartesian coordinates both in
isolation and in groups.

Caleb Levy, 2015.
"""

import abc
from numbers import Real

import numpy as np
import matplotlib.pyplot as plt

from funcstructs.compat import with_metaclass

__all__ = ["Point", "Coordinates"]


class Location2D(with_metaclass(abc.ABCMeta, object)):
    """Abstract coordinates.

    Like all coordinates, they require a representation. The user must
    specify a location's representation in the complex plane, returned
    by the abstract property 'z'. Conversions to Cartesian and Polar
    are provided.
    """

    __slots__ = ()

    @abc.abstractproperty
    def z(self):
        """Locations as points on the complex plane"""
        return 0

    @classmethod
    def from_polar(cls, r, theta):
        """Form points from polar coordinates."""
        return cls(r*np.exp(1j*theta))

    @property
    def x(self):
        """Horizontal components of the Cartesian representation."""
        return self.z.real

    @property
    def y(self):
        """Vertical components of the Cartesian representation."""
        return self.z.imag

    def __abs__(self):
        return np.abs(self.z)

    r = property(__abs__, doc="Radial component of the polar representation.")

    @property
    def theta(self):
        """Angular component of the polar representation"""
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
        if isinstance(other, Real):
            return self.__class__(other*self.z)
        raise TypeError("Cannot multiply coordinates by %s" % type(other))

    def __div__(self, other):
        """inverse of mul"""
        return (1./other) * self

    __truediv__ = __div__

    def rotated(self, angle, origin=0):
        """Locations rotated by given angle about the given origin."""
        coords = self - origin
        r, theta = coords.r, coords.theta
        return self.from_polar(r, theta + angle) + origin


def _check_real_type(xt, yt):
    """Check that xt and yt are subclasses of Real."""
    if not(issubclass(xt, Real) and issubclass(yt, Real)):
        raise TypeError("Expected real coordinates, received %s and %s" %
                        (xt.__name__, yt.__name__))


class Point(Location2D):
    """Point(x, y=None).

    A basic cartesian point. Accepts a single complex number, a single
    (x, y) pair, or two real numbers.

    All of the following are equivalent:
    >>> Point(1, 2)
    >>> Point((1, 2))
    >>> Point(1+2j)
    >>> Point(Point(1, 2))
    """

    __slots__ = "_coord"

    def __init__(self, x, y=None):
        if y is not None:
            _check_real_type(x.__class__, y.__class__)
            z = x + 1j*y
        elif hasattr(x, '__iter__'):
            x, y = x
            _check_real_type(x.__class__, y.__class__)
            z = x + 1j*y
        else:
            z = complex(x)
        self._coord = z

    @property
    def z(self):
        return self._coord

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


class Coordinates(Location2D):
    """Coordinates(x, y=None)

    A Coordinates object represents an ordered collection of points in
    the Cartesian coordinate plane. Coordinates can be constructed
    using either a list of complex numbers and/or pairs or real numbers,
    or two equal length lists containing real numbers, thus:

    >>> Coordinates([(1, 2), (3, 4), (5, 6)])
    >>> Coordinates([1, 3, 5], [2, 4, 6])
    >>> Coordinates([1+2j, 3+4j, 5+6j])

    all compare equal, up to roundoff error.
    """

    __slots__ = "_coords"

    def __init__(self, x, y=None):
        x = np.array(list(x))  # call list since numpy can't take iterables
        if x.ndim != 1:
            raise TypeError("Input must be 1D array of coordinates")
        if y is not None:
            y = np.array(list(y))
            _check_real_type(x.dtype.type, y.dtype.type)
            if x.shape != y.shape:
                raise ValueError("Inputs must be equal length")
            z = x + 1j*y
        else:
            z = x.astype(complex)
        self._coords = z

    @property
    def z(self):
        return self._coords

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

    def rotate(self, angle, origin=0):
        """In place rotation of the array."""
        self._coords = self.rotated(angle, origin).z

    def plot(self, *args, **kwargs):
        """Draw connected sequence of points"""
        if kwargs.get('ax', None) is not None:
            ax = kwargs['ax']
        else:
            ax = plt.gca()
        kwargs.pop('ax', None)
        ax.plot(self.x, self.y, *args, **kwargs)
