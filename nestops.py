#!/usr/bin/env python
# Copyright (C) 2014 Caleb Levy - All Rights Reserved.
# 
# The terms of use, license and copyright information for the code and ideas 
# contained herein are described in the LICENSE file included with this 
# project. For more information please contact me at caleb.levy@berkeley.edu.

from itertools import chain
from iteration import isiterable
from setops import preimage
import unittest

def flatten(listOfLists):
    "Flatten one level of nesting"
    return list(chain.from_iterable(listOfLists))
    
    
def get_nested_el(tree, ind):
    # As long as we can still iterate through tree, continue
    if not isiterable(tree):
        raise ValueError('Tree depth exceeded')
    if not isiterable(ind):
        return tree[ind]
    if len(ind) == 1:
        return tree[ind[0]]
    else:
        return get_nested_el(tree[ind[0]], ind[1:])
    
    
def change_nested_el(tree, ind, el):
    # As long as we can still iterate through tree, continue
    if not isiterable(tree):
        raise ValueError('Tree depth exceeded')
    # Guard against base case of integer index
    if not isiterable(ind):
        tree[ind] = el
    elif len(ind) == 1:
        tree[ind[0]] = el
    else:
        change_nested_el(tree[ind[0]], ind[1:], el)