#!/usr/bin/env python
# Copyright (C) 2014 Caleb Levy - All Rights Reserved.
# 
# The terms of use, license and copyright information for the code and ideas 
# contained herein are described in the LICENSE file included with this 
# project. For more information please contact me at caleb.levy@berkeley.edu.

"""
"""

import unittest
from random import randrange
from endofunctions import endofunctions
import matplotlib.pyplot as plt

randfunc = lambda n: [randrange(n) for I in range(n)]

# N = 10
# It = 100000
# fdist = [0]*N
# for I in range(It):
#     f = randfunc(N)
#     print f
#     fdist[len(set(f))-1] += 1
#
# print fdist
# plt.plot(fdist)
# plt.show()

def get(S):
    for x in S:
        return x
    raise ValueError("Cannot retrieve an item from the empty set")

def modrange(start, stop, modulus):
    for I in range(start,stop):
        yield I%modulus

def funccycles(f, S=None):
    pass
def funccycles(f):
    N = len(f)
    if N == 1:
        return [(0,),]
    cycles = []
    if N == 1:
        return [(0,),]
    for x in range(N):
        path = [x]
        for it in range(N):
            x = f[x]
            path.append(x)
        I = N-1
        while I >= 0 and path[I] != path[-1]:
            I -= 1
        cycles.append(tuple(path[I+1:]))
    return cycles


from endofunctions import endofunctions
class CycleTests(unittest.TestCase):
    funcs = [
             [1,0], 
             [9,5,7,6,2,0,9,5,7,6,2],
             [7,2,2,3,4,3,9,2,2,10,10,11,12,5]
            ]
    N = 20
    funcs += list([randfunc(N) for I in range(100)])
    funcs += list(endofunctions(1))
    funcs += list(endofunctions(3)) + list(endofunctions(4))
    
    def testTuplesAreCycles(self):

        for f in self.funcs:
            c = funccycles(f)
            for cycle in c:
                for ind, el in enumerate(cycle):
                    self.assertEqual(cycle[(ind+1)%len(cycle)], f[el])

if __name__ == '__main__':
    unittest.main()
            
        
    
    

            
            
        