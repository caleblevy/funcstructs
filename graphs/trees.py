#!/usr/bin/env python
# Copyright (C) 2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.

import numpy as np
import matplotlib.pyplot as plt

import graphs


def draw_root_with_leads(n, r=1, h=4, s=4, safety_margin=1.2):
    """Draw n+1 nodes of radius r with one root and the rest a minimum height
    h+2*r centered above the root spaced s+2*r apart."""
    h = (h+2) * r
    s = (s+2) * r
    root_loc = 1j*0.
    half_width = s*(n-1)/2.
    lead_locs = np.linspace(-half_width, half_width, n-1)
    # Ensure the connecting lines to not intersect the nodes.
    safe_height = safety_margin * half_width * r / (1.*s)
    if h < safe_height:
        h = safe_height

    node_locs = np.append([root_loc], 1j*h + lead_locs)
    plt.figure()
    ax = plt.gca()
    graphs.add_nodes(ax, r, node_locs)
    graphs.draw_connections(ax, node_locs, graphs.func_to_vertices([0]*(n)))


if __name__ == '__main__':
    draw_root_with_leads(100)
    plt.show()
