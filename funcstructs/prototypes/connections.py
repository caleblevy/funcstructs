"""Caleb Levy, 2015."""

import numpy as np
import matplotlib.pyplot as plt

from funcgraphs.coordinates import Point
from funcgraphs.line import Line


def circle_points(n, r=1):
    """ Return a list of n points on a circle of radius r in the complex plane
    centered about the origin. """
    w = np.exp(2*np.pi*1j/n)
    points = w**np.arange(n+1)
    return r*points


def complex_to_cart(z):
    """Separate array z into real and imaginary part."""
    x = np.real(z)
    y = np.imag(z)
    return x, y


def node_radius(p, p1, p2, safety_margin=1.5):
    """Compute a node radius less than distance from z to z1-z2."""
    p = Point(p)
    p1 = Point(p1)
    p2 = Point(p2)
    p_int = Line(p1, p2).projection(p)
    side_distance = (p_int - p).r
    vertical_distance = (p1 - p).r
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
        circ_x, circ_y = complex_to_cart(invisible_circle)
        plt.plot(circ_x, circ_y, color='black', visible=False)

        x_pos, y_pos = complex_to_cart(z)
        circ = plt.Circle((x_pos, y_pos), radius=r, color='white', zorder=2)
        circ.set_edgecolor('black')
        ax.add_patch(circ)
        # circ.set_facecolor('w')


def func_to_vertices(f):
    """ Convert list representation of endofunction to Dr. Eppstein's
    dictionary representation. """
    return {i: [f[i]] for i in range(len(f))}


def draw_connections(ax, node_locs, connections):
    """ Draw connections between the ordered points in node_locs. """
    for node, links in connections.items():
        for link in links:
            Line(node_locs[node], node_locs[link]).draw_line()


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
