#! /usr/bin/env python
"""polynomials.py

Enumerate and produce polynomials of various kinds.

Caleb Levy, February 2014. For more information contact caleb.levy@berkeley.edu.
"""
from numpy import ndarray
from rooted_trees import split_set
from sympy import Symbol

# Not sure how to check this one, as there aren't many algorithms to compare against.
def monomial_symmetric_polynomial(x, power_partition):
    """
    Symmetric monomial polynomial formed from the vector x=[x_1,...,x_n] formed from the partition of powers
    partition=[p_1,...,p_l]. It is equivalent to the sum (x[a[1]]**p_1)*(x[a[2]]**p_2)*...*(x[a[I]]**p_l) over all a
    such that a[I] != a[J] for 0<=I<J<=l-1 which are not equivalent under permutation (I think anyway...).

    If there are distinct powers p_1,...,p_j with multiplicities m_1,...,m_j and the list x has n elements then the
    algorithm runs in O(n*m_1*...*m_j) steps, and takes O(m_1*...*m_j) memory in the form of an array of just as many
    dimensions. Inputs may be symbolic, or anything you like.
    """
    n = len(x)
    y, d = split_set(power_partition)
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

def symbol_vector(n):
    x = []
    for I in range(n):
        x.append(Symbol('x%s'%str(I)))
    return x
        
if __name__ == '__main__':
    pass
    