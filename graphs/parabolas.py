#!/usr/bin/env python
# Copyright (C) 2014-2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.

import numpy as np
import matplotlib.pyplot as plt

import graphs


def complex_to_polar(z):
    """Convert complex coordinates to polar coordinates"""
    r = np.abs(z)
    x, y = graphs.complex_to_cart(z)
    theta = np.arctan2(y, x)
    return r, theta


def polar_to_complex(r, theta):
    """Convert polar coordinates to complex coordinates"""
    return r*np.exp(1j*theta)


def polar_to_cart(r, theta):
    """Convert polar coordinates to cartesian coordinates"""
    z = polar_to_z(r, theta)
    x, y = z_to_xy(z)
    return x, y


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
    return z + k


def shorten(r, z1, z2):
    """Shorten the line connecting z_s and z_f by r/2 on each side."""
    vec = z2 - z1
    _, theta = complex_to_polar(vec)
    cut_s = polar_to_complex(r/2., theta)
    cut_f = polar_to_complex(r/2., theta - np.pi)
    z_s -= cut_s
    z_f += cut_f
    return z_s, z_f


def draw_bisecting_line(z1, z2, ax):
    """Draw a line segment perpendicular to z1-z2 of the same length, whose
    center bisects z1-z2."""
    center = (z1 + z2)/2.
    line = np.array([z1, z2]) - center
    r, theta = complex_to_polar(line)
    perp = polar_to_complex(r, theta-np.pi/2.)
    return perp + center


def connecting_parabola(d, z1, z2):
    """ Return a parabola connecting points z1 and z2 with peak distance r away
    from the connecting line. """
    vec = z2 - z1
    r, theta = complex_to_polar(vec)
    parab = parabola(r, d)
    r_p, theta_p = complex_to_polar(parab)
    arrow = polar_to_complex(r_p, theta_p + theta) + z1
    return arrow


def zplot(z):
    """Plot an array of complex numbers by (re(z), im(z))"""
    x, y = graphs.complex_to_cart(z)
    plt.plot(x, y)


if __name__ == '__main__':
    zplot(parabola(4, 2, 0.25))
    z_s1 = 1+1j*2
    z_f1 = 4+1j*7
    r1 = .2

    graphs.draw_connecting_line(z_s1, z_f1, plt.gca())
    zplot(connecting_parabola(r1, z_s1, z_f1))

    z_s2 = 0
    z_f2 = -4-1j*2
    r2 = [-1.5, -1, -.5, 0, .5, 1, 1.5]
    zplot(draw_bisecting_line(z_s2, z_f2, plt.gca()))
    graphs.draw_connecting_line(z_s2, z_f2, plt.gca())
    for i in r2:
        zplot(connecting_parabola(i, z_s2, z_f2))

    plt.show()
