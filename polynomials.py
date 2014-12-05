#! /usr/bin/env python
import numpy as np

def IterativePolynomial(a,part):
    n = len(a)
        
    y = list(set(part))
    l = len(y)
    d = [part.count(y[I]) for I in range(l)]
    
    numf = tuple([I+2 for I in d])
        
    # Contains 1, possibly 2 more dimensions than necessary. Could possibly be rewritten with an inner function, but cost in elegance and practicality deemed not worth it for now.
    T = np.ndarray(numf,object)
    T[:] = 0
    V = [1]*l
    T[tuple(V)] = 1
    
    numf = tuple([I-1 for I in numf])

    for K in range(n-sum(d)+1):
        # Begin the forward march
        go = True
        while go:
            IndX = tuple(V)
            # The recursion itself
            for J in range(l):
                IndXl = V[:]
                IndXl[J] = IndXl[J] - 1
                IndXl = tuple(IndXl)
                T[IndX] = T[IndX] + a[(K-1)+(sum(V)-l)]**y[J]*T[IndXl]
            
            # Counting voodoo
            V[0] = V[0] + 1
            if V[0] > numf[0]:
                V[0] = 1
                go = False
                for I in range(1,l):
                    V[I] = V[I] + 1
                    if V[I] <= numf[I]:
                        go = True
                        break
                    V[I] = 1
                    
    return T[numf]