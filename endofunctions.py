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

def image_path(f):
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

class EndofunctionTest(unittest.TestCase):
    def testImagePath(self):
        """Check various special and degenerate cases, with right index"""
        self.assertEqual([1], image_path([0]))
        self.assertEqual([1], image_path([0,0]))
        self.assertEqual([1], image_path([1,1]))
        self.assertEqual([2], image_path([0,1]))
        self.assertEqual([2], image_path([1,0]))
        node_count = [2,3,5,15]
        for n in node_count:
            tower = [0] + range(n-1)
            cycle = [n-1] + range(n-1)
            fixed = range(n)
            degen = [0]*n
            self.assertEqual(len(range(n)[:0:-1]), n-1)
            self.assertEqual(range(n)[:0:-1], image_path(tower))
            self.assertEqual([n]*(n-1), image_path(cycle))
            self.assertEqual([n]*(n-1), image_path(fixed))
            self.assertEqual([1]*(n-1), image_path(degen))

if __name__ == '__main__':
    unittest.main()
        
        
