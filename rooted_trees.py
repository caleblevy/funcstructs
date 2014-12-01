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
from eppstein.IntegerPartitions import partitions
from itertools import combinations_with_replacement

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

def rooted_trees(N,max_tree=None):
    L = [I+1 for I in range(N)]
    yield tuple(L)
    if max_tree == L:
        return
    while L[1] != L[2]:
        successor(L)
        yield tuple(L)
        if max_tree == L:
            return
            
def split_set(partition):
    # splits a multiset into elements and multiplicities
    y = list(set(partition))
    d = [partition.count(y[I]) for I in range(len(y))]
    return y,d
    
def unpack(tree):
    # Takes a list of lists and outputs a list whose elements are those of the sublists.
    packed_list = [I for I in tree if isinstance(I,(tuple,list,set))]
    unpacked = []
    for I in packed_list:
        for el in I:
            unpacked.append(el)
    return unpacked

def unsplit_set(y, d):
    packed_list = [[y[I]]*d[I] for I in range(len(y))]
    return unpack(packed_list)
    
def 
    
a = [1,1,1,1,2,1,4,3,3,2]
y, d = split_set(a)
print y
print d
aa = unsplit_set(y,d)
print aa

def forests(N):
    for I in rooted_trees(N):
        for J in rooted_trees(N,max_tree=I):
            for K in rooted_trees(N,max_tree=J):
                for L in rooted_trees(N,max_tree=K):
                    yield [I,J,K,L]
                    
def forests2(p4):
    for I in rooted_trees(p4[0]):
        for J in rooted_trees(p4[1],max_tree=I):
            for K in rooted_trees(p4[2],max_tree=J):
                for L in rooted_trees(p4[3],max_tree=K):
                    print [I,J,K,L]
                    
def forests3(p4):
    if len(p4) != 1:
        f = [forests3(p4[:-1])].append()
    
    

if __name__ == '__main__':
    for I in range(3,15):
        print str(I)+':', len(list(rooted_trees(I)))
    
    A = []
    f = []
    for I in rooted_trees(4):
        A = I[:]
        f.append(A)
    print f
    F = rooted_trees(4)
    print len(list(combinations_with_replacement(f,4)))
    print len(list(forests(4)))
    for I in combinations_with_replacement(F,4):
        print tuple(I)
        
    

                    
    
