from primes import divisors
from rooted_trees import split_set, prod
from PADS.IntegerPartitions import partitions
from math import factorial
from fractions import Fraction
import unittest

def binary_partitions(n):
    for part in partitions(n):
        b = [0]*n
        for p in part:
            b[p-1] += 1
        yield b

def burnside_partition_degeneracy(b):
    ss = []
    for i in range(1,len(b)+1):
        s = 0
        for j in divisors(i):
            s += j*b[j-1]
        s **= b[i-1]
        t = Fraction(i,1)
        t **= (-1*b[i-1])
        s *= t
        s /= factorial(b[i-1])
        ss.append(s)
    return prod(ss)
        
def endofunction_count(n):
    tot = 0
    for bp in binary_partitions(n):
        tot += burnside_partition_degeneracy(bp)
    return tot

def ceildiv(a, b):
    """Does long integer division taking the ceiling instead of the floor"""
    return -(-a / b)

def quotient_isint(a, b):
    if a/b == ceildiv(a,b):
        return True
    else:
        return False

def iroot_newton(n, k=2):
    if not n:
        return 0
    u, s = n, n+1
    while u < s:
        s = u
        t = (k-1) * s + n / pow(s, k-1)
        u = t / k
    return s
    
def iroot(n, k=2):
    hi = 1
    while pow(hi, k) < n:
        hi *= 2
    lo = hi / 2
    while hi - lo > 1:
        mid = (lo + hi) // 2
        midToK = pow(mid, k)
        if midToK < n:
            lo = mid
        elif n < midToK:
            hi = mid
        else:
            return mid
            
    if pow(hi, k) == n:
        return hi
    else:
        return lo

def iroot_roundup(n, k=2):
    root = iroot(n,k)
    if pow(root,k) < n:
        return root+1
    else:
        return root
        
def partition_numbers_upto(N):
    if N == 0:
        return [1]
    P = [1]+[0]*N
    for n in range(1,N+1):
        for k in range(1,n+1):
            p_plus = k*(3*k+1)
            p_minus = k*(3*k-1)
            if quotient_isint(p_plus,2) and 1 <= p_plus/2 <= n:
                P[n] += (-1)**(k-1) * P[n-p_plus/2]
            if quotient_isint(p_minus,2) and 1 <= p_minus/2 <= n:
                P[n] += (-1)**(k-1) * P[n-p_minus/2]
    return P

partition_number = lambda n: partition_numbers_upto(n)[-1]

class CounterTest(unittest.TestCase):
    def testIntegerRoots(self):
        for val in range(1000)+range(2**96,2**96+100):
            for power in range(2,5):
                self.assertTrue(iroot(val,power)**power <= val)
                self.assertTrue(val < (iroot(val,power)+1)**power)
                
                self.assertTrue(val <= iroot_roundup(val,power)**power)
                if val > 0:
                    self.assertTrue((iroot_roundup(val,power)-1)**power < val)
                
                self.assertTrue(iroot_newton(val,power)**power <= val)
                self.assertTrue(val < (iroot_newton(val,power)+1)**power)
    
    def testPartitionNumbers(self):
        counts = [1, 1, 2, 3, 5, 7, 11, 15, 22, 30, 42, 56, 77, 101, 135]
        for n in range(len(counts)):
            self.assertEqual(counts[n], partition_number(n))
            

if __name__ == '__main__':
    unittest.main()
    