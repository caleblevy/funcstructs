#!/usr/bin/env python
# Copyright (C) 2014-2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.

import numpy as np
import matplotlib.pyplot as plt


def circle_points(n, r=1):
    """ Return a list of n points on a circle of radius r in the complex plane
    centered about the origin. """
    w = np.exp(2*np.pi*1j/n)
    points = w**np.arange(n+1)
    return r*points


def z_to_xy(z):
    """Separate array z into real and imaginary part."""
    x = np.real(z)
    y = np.imag(z)
    return x, y


def slope_between_points(z1, z2):
    """ Return the slope of the line connecting points z1 and z2 in the complex
    plane. """
    x1, y1 = z_to_xy(z1)
    x2, y2 = z_to_xy(z2)

    m = (y1-y2)/(1.*(x1-x2))
    b = y1 - m*x1
    return m, b


def intersection_point(z, z1, z2):
    """Return the intersection point between the line connecting z1 and z2, and
    the perpendicular to this line passing through z."""
    m1, b1 = slope_between_points(z1, z2)
    x0, y0 = z_to_xy(z)
    m2 = -1./m1  # perpendicular slope to m is -1/m
    b2 = y0 - m2*x0
    x_intersect = (b1-b2)/(1.*(m2-m1))
    y_intersect = m1*x_intersect + b1
    return x_intersect, y_intersect


def node_radius(z, z1, z2, safety_margin=1.5):
    """Compute a node radius less than distance from z to z1-z2."""
    x_int, y_int = intersection_point(z, z1, z2)
    z_int = x_int + 1j*y_int
    side_distance = np.abs(z_int - z)
    vertical_distance = np.abs(z1 - z)
    safe_radius = min([side_distance, vertical_distance])/(1.*safety_margin)
    return safe_radius


def add_nodes(ax, r, node_locs, circ_res=100):
    """ Plot a ring n of circles evenly spaced about the unit circle. """
    circ_points = circle_points(circ_res, r)

    for z in node_locs:
        # Plot invisible copies of the circles to make the plot axes zoom out
        # to contain them. Circle primitives apparently do not necessarily
        # active matplotlib's automatic scaling.
        invisible_circle = circ_points + z
        circ_x, circ_y = z_to_xy(invisible_circle)
        plt.plot(circ_x, circ_y, color='black', visible=False)

        x_pos, y_pos = z_to_xy(z)
        circ = plt.Circle((x_pos, y_pos), radius=r, color='white', zorder=2)
        circ.set_edgecolor('black')
        ax.add_patch(circ)
        # circ.set_facecolor('w')


def func_to_vertices(f):
    """ Convert list representation of endofunction to Dr. Eppstein's
    dictionary representation. """
    return {i: [f[i]] for i in range(len(f))}


def draw_connecting_line(z1, z2, fig):
    """ Add a connecting line between points z1 and z2 to fig. """
    x1, y1 = z_to_xy(z1)
    x2, y2 = z_to_xy(z2)
    x = np.array([x1, x2])
    y = np.array([y1, y2])
    fig.plot(x, y, color='blue', zorder=1)


def draw_connections(ax, node_locs, connections):
    """ Draw connections between the ordered points in node_locs. """
    for node, links in connections.items():
        for link in links:
            draw_connecting_line(node_locs[node], node_locs[link], ax)


def circular_endofunction_graph(func):
    """Given endofunction func, draw the circular graph of its structure."""
    n = len(func)
    node_locs = circle_points(n)[0:n]  # represent the function circularly.
    r = node_radius(node_locs[1], node_locs[0], node_locs[2])
    connections = func_to_vertices(func)

    plt.figure(1)
    ax = plt.gca()

    add_nodes(ax, r, node_locs)
    draw_connections(ax, node_locs, connections)


if __name__ == '__main__':
    circular_endofunction_graph([0, 0, 1, 1, 2, 4, 5, 5, 7, 8, 9])
    plt.show()
