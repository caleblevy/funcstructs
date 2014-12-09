# from iteration import product_range
import unittest

endofunctions = lambda n: product_range([n]*n)
def image_path(f):
    """TODO: Unit test this MOFO"""
    card = card_prev = len(set(f))
    f_orig = f[:]
    cardinalities = [card]
    it = 0
    for it in range(1,len(f)-2):
        f = [f_orig[x] for x in f]
        card = len(set(f))
        cardinalities.append(card)
        if card == card_prev:
            break
        card_prev = card
    cardinalities.extend([card]*(len(f)-it-2))
    return cardinalities

f = [0,0,1,2,3,4,5,6,7,8,9,10,11]
print image_path(f)
print len(f)
print(len(image_path(f)))
g = [0,1]
h = [0]
l = [0,0]
print image_path(g)
print image_path(h)
print image_path(l)
print image_path([0,0,1,2,4,3,5,6,7,7])
print len(image_path([0,0,1,2,4,3,5,6,7,8]))
print [0,0,0,0,0,0,0,0,0]
print len([0,0,0,0,0,0,0,0,0])
[1,2,3,4,5,4,3,2,1,0]
print len(image_path([1,2,3,4,5,4,3,2,1,0]))
print image_path([0,0,0,0,0,0,0,0,0])

# class 
        
