# from iteration import product_range
import unittest

endofunctions = lambda n: product_range([n]*n)
def image_path_naive(f):
    """TODO: Unit test this MOFO"""
    cardinalities = []
    f_orig = f[:]
    for it in range(len(f_orig)-1):
        cardinalities.append(len(set(f)))
        f = [f_orig[x] for x in f]
    return cardinalities

image_path_naive([0]+range(15))

print image_path_naive([0]+range(-1))

def image_path(f):
    n = len(f)
    cardinalities = []
    f_orig = f[:]
    card_prev = n
    for it in range(n-1):
        card = len(set(f))
        cardinalities.append(len(set(f)))
        f = [f_orig[x] for x in f]
        if card == card_prev:
            cardinalities.extend([card]*(n-2-it))
            break
        card_prev = card
    return cardinalities
        
        

f = [0,0,1,2,3,4,5,6,7,8,9,10,11]
g = [0,0,0,1,2,3,4,5,6,7,8,9,10,11]
print image_path(f)
print image_path_naive(f)
print image_path(g)
print image_path_naive(g)

class EndofunctionTest(unittest.TestCase):
    def testImagePath(self):
        """Check various special and degenerate cases, with right index"""
        node_count = [1,3,5,15]
        for n in node_count:
            tower = [0] + range(n-1)
            cycle = [n-1] + range(n-1)
            fixed = range(n)
            degen = [0]*n
            print range(n)[:0:-1]
            self.assertEqual(range(n)[:0:-1], image_path(tower))
            self.assertEqual([n]*(n-1), image_path(cycle))
            self.assertEqual([n]*(n-1), image_path(fixed))
            self.assertEqual([1]*(n-1), image_path(degen))

if __name__ == '__main__':
    unittest.main()
    pass
        
        
