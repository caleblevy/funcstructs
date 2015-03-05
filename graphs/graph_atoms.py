#!/usr/bin/env python
import numpy as np
import matplotlib.pyplot as plt
import pylab

def Z_to_XY(z):
    x = np.real(z)
    y = np.imag(z)
    return x,y

def Z_to_RT(z):
    r = np.abs(z)
    x,y = Z_to_XY(z)
    theta = np.arctan2(y,x)
    return r,theta
    
def RT_to_Z(r,theta):
    return r*np.exp(1j*theta)

def RT_to_XY(r,theta):
    z = RT_to_Z(r,theta)
    x = np.real(z)
    y = np.imag(z)
    return x,y
    
def Base_Parab(sep,h, cut_short=0., N_Points=100): # Basic, symmetric, parabola, used to construct more general type
    k = sep/2.
    x_s = cut_short - k
    x_f = k - cut_short
    x = np.linspace(x_s,x_f,N_Points)
    y = -h/k**2 * (x + k) * (x - k)
    z_Parab = x + 1j*y
    return z_Parab + k
    
def Shorten_Line(z_s,z_f,r):
    vec = z_f - z_s
    dist,theta = Z_to_RT(vec)
    cut_s = RT_to_Z(r/2.,theta)
    cut_f = RT_to_Z(r/2.,theta-np.pi)
    
    z_s -= cut_s
    z_f += cut_f
    return z_s,z_f
    

def Base_Line(z_s,z_f,N_Points=100):
    m = z_f - z_s
    t = np.linspace(0.,1.,N_Points)
    line = m*t + z_s
    return line

def Perp_Line(z_s,z_f,N_Points=100):
    line = Base_Line(z_s,z_f)
    line -= (z_f + z_s)/2.
    r,theta = Z_to_RT(line)
    perp = RT_to_Z(r,theta-np.pi/2)
    perp += (z_f + z_s)/2.
    return perp

def Arrow_Parab(z_s,z_f,r):
    vec = z_f - z_s
    dist,theta = Z_to_RT(vec)
    parab = Base_Parab(dist,r)
    r_p,theta_p = Z_to_RT(parab)
    arrow = RT_to_Z(r_p,theta_p + theta) + z_s
    return arrow
    
def Z_to_Plot(z):
    x,y = Z_to_XY(z)
    plt.plot(x,y)
    
z_s1 = 1+1j*2
z_f1 = 4+1j*7
r1 = .2
Z_to_Plot(Base_Line(z_s1,z_f1))
Z_to_Plot(Arrow_Parab(z_s1,z_f1,r1))

z_s2 = 0
z_f2 = -4-1j*2
r2 = [-1.5,-1,-.5,0,.5,1,1.5]
Z_to_Plot(Perp_Line(z_s2,z_f2))
Z_to_Plot(Base_Line(z_s2,z_f2))
for I in r2:
    Z_to_Plot(Arrow_Parab(z_s2,z_f2,I))

pylab.show()
print 5
a = 4
print a