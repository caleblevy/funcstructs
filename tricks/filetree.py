#!/usr/bin/env python
# Copyright (C) 2014-2015 Caleb Levy - All Rights Reserved.
#
# The terms of use, license and copyright information for the code and ideas
# contained herein are described in the LICENSE file included with this
# project. For more information please contact me at caleb.levy@berkeley.edu.

import os

from endofunction_structures import rootedtrees


def directory_level_sequence(directory, level=1):
    """Return the level sequence of the ordered unlabelled tree corresponding
    to the specified directory."""
    level_sequence = [level]
    for f in os.listdir(directory):
        fpath = os.path.join(directory, f)
        if os.path.isfile(fpath):
            level_sequence.append(level+1)
        else:
            level_sequence.extend(directory_level_sequence(fpath, level+1))
    return level_sequence


def directory_tree(directory):
    """Return the ordered tree corresponding to the file system directory
    structure."""
    level_sequence = os.path.abspath(os.path.expanduser(directory))
    return rootedtrees.OrderedTree(directory_level_sequence(folder))


if __name__ == '__main__':
    t = directory_level_sequence(os.path.abspath(os.path.expanduser(
        '~/interesting_repos/linux'))
    )
    tree = rootedtrees.DominantTree(t)
    print "Level representation: ", tree
    print "Unordered representation: ", tree.unordered()
    print "Degeneracy: ", tree.degeneracy()
    print "Degeneracy size: ", len(str(tree.degeneracy()))
    print "Number of nodes: ", len(tree)
