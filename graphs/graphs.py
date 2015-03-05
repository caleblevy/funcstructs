#!/usr/bin/env python
import numpy as np
import matplotlib.pyplot as plt
import math
import pylab


Func = [0,0,1,1,2,4,5,5,7,8,9]
n = len(Func)
cRes = 100


def CircPoints(n,r=1):
    W = np.exp(2*np.pi*1j/n)
    cPoints = W**np.arange(n+1)
    return cPoints*r
    
Node_List = CircPoints(n)[0:n] # Cut the last point
FuncG = plt.figure(1)

def Z_to_XY(z):
    x = np.real(z)
    y = np.imag(z)
    return x,y

def PntToSlope(z1,z2):
    x1,y1 = Z_to_XY(z1)
    x2,y2 = Z_to_XY(z2)

    m = (y1-y2)/(x1-x2)
    b = y1 - m*x1
    return m,b
    
def Intersect(z1,z2,z):
    m1,b1 = PntToSlope(z1,z2)
    x0,y0 = Z_to_XY(z)
    
    m2 = -1/m1
    b2 = y0 - m2*x0
    x_int = (b1-b2)/(m2-m1)
    y_int = m1*x_int + b1
    return x_int,y_int
    
def Node_Radius(Node_List):
    z1 = Node_List[0]
    z2 = Node_List[2]
    z = Node_List[1]
    
    x_s,y_s = Intersect(z1,z2,z)
    z_int = x_s + 1j*y_s
    Side_Bound = np.abs(z_int-z)
    Vert_Bound = np.abs(z1-z)
    rCirc = np.min([Vert_Bound,Side_Bound])/1.5
    return rCirc

rCirc = Node_Radius(Node_List)

def Add_Node_Ax(FuncG,Node_List):
    rCirc = Node_Radius(Node_List)
    Circ_Points = CircPoints(cRes,rCirc)
    plt.figure(FuncG.number)
    
    for I in Node_List:
        circ = Circ_Points + I
        circ_x, circ_y = Z_to_XY(circ)
        plt.plot(circ_x,circ_y,color='black',visible=False)
    return rCirc
        
def Add_Nodes(FuncG,Node_List):
    rCirc = Node_Radius(Node_List)
    plt.figure(FuncG.number)
    FuncAx = plt.gca()
    
    for z in Node_List:
        circ_x,circ_y = Z_to_XY(z)
        circ = plt.Circle((circ_x,circ_y),radius=rCirc,color='white',zorder=2)
        circ.set_edgecolor('black')
        FuncAx.add_patch(circ)
        # circ.set_facecolor('w')
        
    return rCirc
    
def FuncToSet(Func):
    n = len(Func)
    if n <= np.max(Func):
        raise ValueError('Not a self-map')
    FuncSet = [tuple([I,tuple([Func[I]])]) for I in range(n)]
    return FuncSet

def PlotPoints(FuncAx,z1,z2):
    x1,y1 = Z_to_XY(z1)
    x2,y2 = Z_to_XY(z2)
    x = np.array([x1,x2])
    y = np.array([y1,y2])
    FuncAx.plot(x,y,color='blue',zorder=1)
    
def Z_to_RA(z):
    x,y = Z_to_XY(z)
    r = np.abs(z)
    theta = np.arctan2(y,x)
    return r,theta

def RA_to_XY(r,theta):
    z = r*np.exp(1j*theta)
    x = np.real(z)
    y = np.imag(z)
    return x,y
    
def Add_Arrows(FuncAx,z1,z2,rCirc):
    vec = z2-z1
    r,theta = Z_to_RA(vec)
    
    z1 += (r/2)*np.exp(1j*theta)
    z2 += (r/2)*np.exp(-1j*theta)
    
    
    r1,theta1 = Z_to_RA(z1)
    r2,theta2 = Z_to_RA(z2)
    
     

def Add_Connections(FuncG,Node_List,Connections):
    if isinstance(Connections[0],int):
        Connections = FuncToSet(Connections)
    plt.figure(FuncG.number)
    FuncAx = plt.gca()
    for Node in Connections:
        v = Node_List[Node[0]]
        MultIm = Node[1]
        for El in MultIm:
            u = Node_List[El]
            PlotPoints(FuncAx,u,v)
            

        
    
Circ_Points = Add_Node_Ax(FuncG,Node_List)
Add_Nodes(FuncG,Node_List)
Add_Connections(FuncG,Node_List,Func)

pylab.show()

