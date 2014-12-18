"""endofunctions.py

Let S be a finite set with N elements; i.e. |S|=N. There are N^N endofunctions defined on this set, and we shall denote the set of all such objects by S^S. 

For a given f in S^S, its image will have n=|f(S)| elements for n in range(1,N+1). Similarly it's second iterate will have |f(f(S))|=m<=n elements. Once |f^(k)(S)|=|f^(k+1)(S)| then |f^(j)(S)|=|f^(k)(S)| for k>j. The list of sizes of images of iterates of f from 1 to n-1 is called the "image path" of f.

This file mainly exists to calculate the distribution of image sizes of the iterates of all endofunctions on a set S. The naive way to do this is to literally enumerate every endofunction. This works for n up to about 8 on a decent desktop computer.

The second, far more efficient method, is to enumerate the endofunction structures on S (i.e. orbits of the transformation monoid under the action of conjugation by the symmetric group). This runs in roughly O(4^n) time. This is still quite horrendous, but it enables us to get up to n=16 before being intolerably slow.

Various special cases can be done much faster. This distribution of (first iterate) image sizes can be done in O(n^2) and the final set can be O(n).

"""

from iteration import product_range, compositions
from endofunction_structures import endofunction_structures, structure_multiplicity, endofunction_to_func
import numpy as np
import unittest
from math import factorial
from necklaces import nCk

endofunctions = lambda n: product_range([n]*n)

def imagepath(f):
    """
    Given a list f of length n such that all([I in range(n) for I in f]), 
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

def iterate_imagedist_brute(n):
    """
    The most naive, straightforward way to calculate the distribution of 
    """
    M = np.zeros((n,n-1), dtype=object)
    for f in endofunctions(n):
        im = imagepath(f)
        for it, card in enumerate(im):
            M[card-1,it] += 1
    return M

def iterate_imagedist_endofunction(n):
    if n == 1:
        return np.array([1],dtype=object)
        
    M = np.zeros((n,n-1), dtype=object)
    for func_struct in endofunction_structures(n):
        mult = structure_multiplicity(func_struct)
        f = endofunction_to_func(func_struct)
        im = imagepath(f)
        for it, card in enumerate(im):
            M[card-1,it] += mult
    return M

iterate_imagedist = iterate_imagedist_endofunction

def firstdist_composition(n):
    """
    Count OEIS A090657 using integer compositions in O(2^n) time
    """
    if n == 1:
        return [1]
        
    F = [0]*n
    # Saves factor of 2 there.
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

def firstdist_recurse(n):
    """
    Count OEIS A090657 using recursion relation in O(n^2) time. This is the fastest method I know of and probably the fastest there is.
    
    # TODO - Figure out the logic that went into this and the previous one and latex it up.
    """
    FD = np.zeros((n,n),dtype=object)
    FD[0,0] = 1
    F = np.array([1],dtype=object)
    for I in range(1,n):
        F_Old = F
        F = np.zeros(I+1,dtype=object)
        # Set the boundaries
        F[0] = 1; FD[0,I] = I+1
        F[I] = 1; FD[I,I] = factorial(I+1)
        for J in range(1,I):
            F[J] = F_Old[J-1] + (J+1)*F_Old[J]
            FD[J,I] = factorial(I+1)/factorial(I-J)*F[J]
    return list(FD[:,-1])
    
firstdist = firstdist_recurse

'''
Top row: OEIS A236396 - labelled rooted trees of height at most k on n nodes
Right column: OEIS A066324, A219694 (reverse), A243203
'''

def lastdist_comp(n):
    L = [factorial]

class EndofunctionTest(unittest.TestCase):
    iterate_imagedists = [
        np.array([[3, 9],
                  [18, 12],
                  [6, 6]],
                  dtype=object),
                  
        np.array([[4, 40, 64,],
                  [84, 120, 96],
                  [144, 72, 72],
                  [24, 24, 24]],
                  dtype=object),
                  
        np.array([[5, 205, 505, 625],
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
        
    def testImagepath(self):
        """Check various special and degenerate cases, with right index"""
        self.assertEqual([1], imagepath([0]))
        self.assertEqual([1], imagepath([0,0]))
        self.assertEqual([1], imagepath([1,1]))
        self.assertEqual([2], imagepath([0,1]))
        self.assertEqual([2], imagepath([1,0]))
        node_count = [2,3,5,15]
        for n in node_count:
            tower = [0] + range(n-1)
            cycle = [n-1] + range(n-1)
            fixed = range(n)
            degen = [0]*n
            self.assertEqual(range(n)[:0:-1], imagepath(tower))
            self.assertEqual([n]*(n-1), imagepath(cycle))
            self.assertEqual([n]*(n-1), imagepath(fixed))
            self.assertEqual([1]*(n-1), imagepath(degen))
    
    def testIterateImagedist(self):
        """Check the star of the show; an exponential time algorithm for finding the multiplicities of image"""
        for dist in self.iterate_imagedists:
            n = dist.shape[0]
            np.testing.assert_array_equal(dist, iterate_imagedist_brute(n))
            np.testing.assert_array_equal(dist, iterate_imagedist_endofunction(n))
    
    def testFirstdist(self):
        """Left column: OEIS A101817 (A090657). Test number of endofunctions on n elements whose image has size k."""
        for dist in self.firstdists:
            n = len(dist)
            print n
            self.assertEqual(dist, firstdist_composition(n))
            self.assertEqual(dist, list(iterate_imagedist(n)[:,0]))
            self.assertEqual(dist, firstdist_recurse(n))
        

if __name__ == '__main__':
    unittest.main()
        
        
