from primes import divisors
from rooted_trees import split_set, prod
from PADS.IntegerPartitions import partitions
from math import factorial
from fractions import Fraction

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
    
