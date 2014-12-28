#!/usr/bin/env python
# Copyright (C) 2014 Caleb Levy - All Rights Reserved.
# 
# The terms of use, license and copyright information for the code and ideas 
# contained herein are described in the LICENSE file included with this 
# project. For more information please contact me at caleb.levy@berkeley.edu.

"""
Enumerate and produce polynomials of various kinds.

Caleb Levy, February 2014. For more information contact caleb.levy@berkeley.edu.
"""
from numpy import ndarray
from rooted_trees import split_set
from sympy import Symbol
import unittest

# MSP == Monomial Symmetric Polynomial
def MSP_recursive(x, powers):
    # Wrapper for _recursive_monomial_alg which separates the multiset powers into elements with degeneracies, and returns the value fo the function
    y, d = split_set(powers)
    return _recursive_monomial_alg(x, d, y)

def _recursive_monomial_alg(x, d, y):
    """_recursive_monomial_alg(x, d, y)

    Recursive version of the general formula for evaluating symmetric
    monomial polynomials. This one, while inefficient, is certainly in some
    sense elegant, and is written as such for that reason.

    This function itero-recursive and HIGHLY inefficient, duplicating an extraordinary amount of work. It exists as a
    showcase of the concepts behind MSP_iterative. Its running time might be something like len(y)^len(x), but either
    way, do not run this thing with input vectors of length greater than about 5 ot 10, depending on your system.

    X = (a1,a2,...,an) - Vector of values for polynomial evaluation
    D = (d1,d2,...,dl) - Vector of degeneracies of exponent partitions
    Y = (y1,y2,...,yl) - Vector of exponents.

    Premise of formula is given by:
       T(n,d1,...,dl) = T(n-1,d1,...,dl) + an^y1*T(n-1,d1-1,...,dl) + ...
                           ... + an^yl*T(n-1,d1,...,dl-1).
                           
    D and Y need to be of same length.
    """
    # This is the matlab copy version
    if any(I<0 for I in d):
        return 0
    elif not x:   
        if all(I==0 for I in d):
            return 1
        else:
            return 0
    else:
        val = _recursive_monomial_alg(x[:-1],d,y)        
        for I in range(len(d)):
            d_temp = d[:]
            d_temp[I] -= 1
            val += x[-1]**y[I]*_recursive_monomial_alg(x[:-1],d_temp,y)               
        return val

# Not sure how to check this one, as there aren't many algorithms to compare against.
def MSP_iterative(x, powers):
    """
    Symmetric monomial polynomial formed from the vector x=[x_1,...,x_n] formed from the partition of powers
    partition=[p_1,...,p_l]. It is equivalent to the sum (x[a[1]]**p_1)*(x[a[2]]**p_2)*...*(x[a[I]]**p_l) over all a
    such that a[I] != a[J] for 0<=I<J<=l-1 which are not equivalent under permutation (I think anyway...).

    If there are distinct powers p_1,...,p_j with multiplicities m_1,...,m_j and the list x has n elements then the
    algorithm runs in O(n*m_1*...*m_j) steps, and takes O(m_1*...*m_j) memory in the form of an array of just as many
    dimensions. Inputs may be symbolic, or anything you like.
    """
    n = len(x)
    y, d = split_set(powers)
    l = len(y)
    shape = tuple([I+2 for I in d])
        
    # Contains 1, possibly 2 more dimensions than necessary.
    T = ndarray(shape, object)
    T[:] = 0
    V = [1]*l
    T[tuple(V)] = 1
    
    shape = tuple([I-1 for I in shape])
    
    # The powers use up sum(multiplcities) of the original x.
    for K in range(n-sum(d)+1):
        # Begin the forward march
        go = True
        while go:
            ind = tuple(V)
            # The recursion itself
            for J in range(l):
                ind_last = V[:]
                ind_last[J] -= 1
                ind_last = tuple(ind_last)
                T[ind] += x[(K-1)+(sum(V)-l)]**y[J]*T[ind_last]
            
            # Counting voodoo. Could be replaced with itertools.product, but then we would have type conversions.
            V[0] = V[0] + 1
            if V[0] > shape[0]:
                V[0] = 1
                go = False
                for I in range(1,l):
                    V[I] = V[I] + 1
                    if V[I] <= shape[I]:
                        go = True
                        break
                    V[I] = 1                    
    return T[shape]

monomial_symmetric_polynomial = MSP_iterative

def symrange(*args):
    x = []
    for I in range(*args):
        x.append(Symbol('x%s'%str(I)))
    return x
class PolynomialTest(unittest.TestCase):
    def testMonomialSymmetricPolynomial(self):
        x = symrange(14)
        # p = 
        


        
if __name__ == '__main__':
    print MSP_recursive([5,5,5],[3,3,2])
    print monomial_symmetric_polynomial([5,5,5],[3,3,2])
    print monomial_symmetric_polynomial(symrange(14),[3,3,2]).expand()

    