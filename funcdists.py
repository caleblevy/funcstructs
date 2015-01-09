#!/usr/bin/env python
# Copyright (C) 2013, 2014 and 2015 Caleb Levy - All Rights Reserved.
# 
# The terms of use, license and copyright information for the code and ideas 
# contained herein are described in the LICENSE file included with this 
# project. For more information please contact me at caleb.levy@berkeley.edu.

"""
Let S be a finite set with N elements; i.e. |S|=N. There are N^N endofunctions
defined on this set, and we shall denote the set of all such objects by S^S.

For a given f in S^S, its image will have n=|f(S)| elements for 1 <= n <= N.
Similarly its second iterate will have |f(f(S))|=m<=n elements. Once
|f^(k)(S)|=|f^(k+1)(S)| then |f^(j)(S)|=|f^(k)(S)| for all j>k. The list of
sizes of images of iterates of f from 1 to n-1 is called the "image path" of f.

This file mainly exists to calculate the distribution of image sizes of the
iterates of all endofunctions on a set S. The naive way to do this is to
literally enumerate every endofunction. This works for n up to about 8 on a
decent desktop computer.

The second, far more efficient method, is to enumerate the endofunction
structures on S (i.e. orbits of the full transformation monoid under the action
of conjugation by the symmetric group), and then add up the multiplicities of
each structure. This runs in roughly O(4^n) time. This is still quite
horrendous, but it enables us to get up to n=16 before being intolerably slow.

Various special cases can be done much faster. This distribution of (first
iterate) image sizes can be done in O(n^2) and the distribution of last iterate
image sizes set can be O(n) (and has a lovely closed form formula).
"""

from funcstructs import funcstructs, funcstruct_degeneracy, funcstruct_to_func,\
                        funcstruct_imagepath
from iteration import product_range, compositions
from math import factorial
from necklaces import nCk
import numpy as np
import unittest


endofunctions = lambda n: product_range([n]*n)

def imagepath(f):
    """
    Give it a list so that all([I in range(len(f)) for I in f]) and this
    program spits out the image path of f.
    """
    n = len(f)
    cardinalities = [len(set(f))]
    f_orig = f[:]
    card_prev = n
    for it in range(1,n-1):
        f = [f_orig[x] for x in f]
        card = len(set(f))
        cardinalities.append(len(set(f)))
        if card == card_prev:
            cardinalities.extend([card]*(n-2-it))
            break
        card_prev = card
    return cardinalities


def imagedist_brute(n):
    """
    The most naive, straightforward way to calculate the distribution of
    endofunctions is to count every endofunction. Although absurdly simple, and
    computationally infeasible, it is the only true way to check your work.
    """
    M = np.zeros((n,n-1), dtype=object)
    for f in endofunctions(n):
        im = imagepath(f)
        for it, card in enumerate(im):
            M[card-1,it] += 1
    return M


def imagedist_endofunction(n):
    """
    To count distributions of image sizes, we don't really need every function,
    since pretty much every meaningful aspect of a function's structure is
    encoded by it's unlabeled directed graph.
    
    It is relatively straightforward to determine the multiplicity of a
    function graph (Note: for various definitions of "straightforward". Yours
    may differ considerably). If you know the imagesize distribution for
    canonical functions of each structure, and their multiplicities, you can
    simply enumerate structures and add that multiplicity to the image path.

    That is the outline of this program:
    - For each endofuction structure:
        1) Determine the multiplicity of the structure
        2) Convert the structure to a function
        3) Calculate the image path of that function
        4) Add that multiplicity to each point in the distribution
           corresponding to that iterate image size.

    Runs in O(4^n) time (since there are ~4^n structures on n elements). Proof
    will be in the "notes" section.
    """
    if n == 1:
        return np.array([1],dtype=object)
        
    M = np.zeros((n,n-1), dtype=object)
    nfac = factorial(n)
    for struct in funcstructs(n):
        mult = nfac//funcstruct_degeneracy(struct)
        im = funcstruct_imagepath(struct)
        for it, card in enumerate(im):
            M[card-1,it] += mult
    return M

imagedist = imagedist_endofunction


def firstdist_composition(n):
    """
    Produces left column of imagedist using integer compositions in O(2^n) time.
    
    The idea of the agorithm comes from a binary tree. Need to find it.
    """
    if n == 1:
        return [1]
        
    F = [0]*n
    for comp in product_range([2]*(n-1)):
        val = n
        rep = 1
        for I in comp:
            if not I:
                val *= rep
            else:
                val *= n - rep
                rep += 1
        F[rep-1] += val
    return F


def firstdists_upto(N):
    """
    Left column of imagedist. This uses a recursion relation to run in O(n^2)
    time. This is the fastest method I know of and probably the fastest there
    is.

    # TODO - Figure out the logic that went into this and the previous one and
    latex it up. Derived from the ideas in the first one.
    """
    FD = np.zeros((N,N), dtype=object)
    for n in range(N):
        FD[0,n] = FD[n,n] = 1
        for I in range(n):
            FD[I,n] = FD[I-1,n-1] + (I+1)*FD[I,n-1]
    
    for n in range(N):
        for I in range(n+1):
            FD[I,n] *= factorial(n+1)//factorial(n-I)

    return FD
    
firstdist_recurse = firstdist = lambda n: list(firstdists_upto(n)[:,-1])


def nCk_grid(N):
    """nCk(n,k) == nCk_table[n,k] for 0 <= k <= n <= N"""
    binomial_coeffs = np.zeros((N+1, N+1), dtype=object)
    for I in range(N+1):
        for J in range(N+1):
            if J > I:
                continue
            binomial_coeffs[I,J] = nCk(I,J)
    return binomial_coeffs


def powergrid(N):
    """I**J == powergrid[I,J] for 0 <= I, J <= N. Note 0^0 defined as 1."""
    base = np.arange(N+1, dtype=object)
    [bases, exponents] = np.meshgrid(base, base)
    exponentials = bases**exponents
    return exponentials.T
           
                
def lastdist_composition(N):
    L = [0]*N
    # Memoize these lookups; saves a lot of time.
    exponentials = powergrid(N)
    binomial_coefficients = nCk_grid(N)
    for comp in compositions(N):
        val = 1
        for J in range(1,len(comp)):
            val *= exponentials[comp[J-1], comp[J]]
            val *= binomial_coefficients[sum(comp[J:]), comp[J]]
        L[comp[0]-1] += val
    for n in range(N,0,-1):
        L[n-1] *= factorial(N)//factorial(N-n)
    return L   
    
    
def limitset_count(n,k):
    return k*n**(n-k)*factorial(n-1)//factorial(n-k)


def limitset_direct(n):
    return [limitset_count(n,k) for k in range(1,n+1)]

def limitset_recurse(n):
    L = [n**(n-1)]+[0]*(n-1)
    for k in range(1,n):
        L[k] = (L[k-1]*(k+1)*(n-k))//(k*n)
    return L
    
limitset = limitset_recurse
                
class EndofunctionTest(unittest.TestCase):
    imagedists = [
        np.array([
            [3, 9],
            [18, 12],
            [6, 6]],
            dtype=object),
                  
        np.array([
            [4, 40, 64,],
            [84, 120, 96],
            [144, 72, 72],
            [24, 24, 24]],
            dtype=object),
                  
        np.array([
            [5, 205, 505, 625],
            [300, 1060, 1120, 1000],
            [1500, 1260, 900, 900],
            [1200, 480, 480, 480],
            [120, 120, 120, 120]], 
            dtype=object)
    ]
    
    firstdists = [
        [2,2],
        [3,18,6],
        [4,84,144,24],
        [5,300,1500,1200,120],
        [6,930,10800,23400,10800,720],
        [7,2646,63210,294000,352800,105840,5040]
    ]
    
    lastdists = [
        [2,2],
        [9,12,6],
        [64,96,72,24],
        [625,1000,900,480,120],
        [7776,12960,12960,8640,3600,720],
        [117649,201684,216090,164640,88200,30240,5040]
    ]
    
    treefuncs = [
        [3, 9],
        [4, 40, 64],
        [5, 205, 505, 625],
        [6, 1176, 4536, 7056, 7776],
        [7, 7399, 46249, 89929, 112609, 117649],
        [8, 50576, 526352, 1284032, 1835072, 2056832, 2097152]
    ]
     
        
    def testImagepath(self):
        """Check various special and degenerate cases, with right index"""
        self.assertEqual([1], imagepath([0]))
        self.assertEqual([1], imagepath([0,0]))
        self.assertEqual([1], imagepath([1,1]))
        self.assertEqual([2], imagepath([0,1]))
        self.assertEqual([2], imagepath([1,0]))
        node_count = [2,3,5,15]
        for n in node_count:
            tower = [0] + list(range(n-1))
            cycle = [n-1] + list(range(n-1))
            fixed = list(range(n))
            degen = [0]*n
            self.assertEqual(list(range(n)[:0:-1]), imagepath(tower))
            self.assertEqual([n]*(n-1), imagepath(cycle))
            self.assertEqual([n]*(n-1), imagepath(fixed))
            self.assertEqual([1]*(n-1), imagepath(degen))
    
    
    def testFuncstructImagepath(self):
        """Verify equivalence of methods for computing structure image paths."""
        N = 8
        for n in range(1,N):
            for struct in funcstructs(n):
                im = imagepath(funcstruct_to_func(struct))
                imstruct = funcstruct_imagepath(struct)
                np.testing.assert_array_equal(im, imstruct)
                
                
    def testIterateImagedist(self):
        """Check the multiplicities of sizes of images of iterates."""
        for dist in self.imagedists:
            n = dist.shape[0]
            np.testing.assert_array_equal(dist, imagedist_brute(n))
            np.testing.assert_array_equal(dist, imagedist_endofunction(n))
    
    
    def testSingularImages(self):
        '''
        OEIS A236396: labelled rooted trees of height at most k on n nodes.
        Corresponds to the top row of imagedist.
        '''
        for dist in self.treefuncs:
            n = len(dist) + 1
            np.testing.assert_array_equal(dist, imagedist_endofunction(n)[0,:])
    
    
    def testFirstdist(self):
        """
        OEIS A101817: T(n,h) = number of functions f:{1,2,...,n}->{1,2,...,n}
        such that |Image(f)|=h; h=1,2,...,n, n=1,2,3,...
        """
        for dist in self.firstdists:
            n = len(dist)
            self.assertEqual(dist, firstdist_composition(n))
            self.assertEqual(dist, list(imagedist(n)[:,0]))
            self.assertEqual(dist, firstdist_recurse(n))
        
        
    def testBinomialgrid(self):
        """Check that nCk(n,k) == nCk_table[n,k] for 0 <= k <= n <= N"""
        N = 20
        binomial_coefficients = nCk_grid(N)
        for n in range(N+1):
            for k in range(n+1):
                self.assertEqual(nCk(n,k), binomial_coefficients[n,k])


    def testPowergrid(self):
        """I**J == powergrid[I,J] for 0 <= I, J <= N. Note 0^0 defined as 1."""
        N = 20
        exponentials = powergrid(N)
        for I in range(N+1):
            for J in range(N+1):
                if I == J == 0:
                    self.assertEqual(1, exponentials[I,J])
                else:
                    self.assertEqual(I**J, exponentials[I,J])
    
    
    def testLastdist(self):
        """
        OEIS A066324: Number of endofunctions on n labeled points constructed
        from k rooted trees.
        """
        for dist in self.lastdists:
            n = len(dist)
            self.assertEqual(dist, lastdist_composition(n))
            self.assertEqual(dist, list(imagedist(n)[:,-1]))
            self.assertEqual(dist, limitset_direct(n))
            self.assertEqual(dist, limitset_recurse(n))
            

if __name__ == '__main__':
    unittest.main()
