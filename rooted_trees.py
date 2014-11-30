#!/usr/bin/env python
"""
Contains  one main  function:  rooted_trees. Takes  an integer  N  as input  and
outputs a generator object enumerating  all isomorphic unlabeled rooted trees on
N nodes. Consult OEIS A000055 to find len(list(rooted_trees(N))).

Copyright (C) 2014 Caleb Levy - All Rights Reserved.
The terms  of non-commercial usage of  this code are simply  providing credit of
some variety,  either in the  typical list of  contributors section of  the code
repository or,  if used for an  academic paper, some contribution  in the paper.
For commercial use, please contact me at caleb.levy@berkeley.edu.
"""
def successor(L):
    N = len(L)
    p = N-1
    while L[p] == L[1]:
        p -= 1
    q = p-1
    while L[q] >= L[p]:
        q -= 1
    for I in range(p,N):
        L[I] = L[I-(p-q)]

def rooted_trees(N):
    L = [I+1 for I in range(N)]
    yield L
    while L[1] != L[2]:
        successor(L)
        yield L
if __name__ == '__main__':
    for K in range(3,15):
        print str(K)+':', len(list(rooted_trees(K)))