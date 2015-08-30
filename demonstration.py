#' % Demonstration of Funcstructs
#' % Caleb Levy
#' % June 2015

#' # Continuous Functions

#' Consider the function $f(x) = x^2$ defined on the half-closed interval
#' $[0,1)$. It is plotted below.

from __future__ import print_function

import numpy as np
import matplotlib.pyplot as plt
import pylab

from funcstructs.utils import split
from funcstructs.structures import randconj, Funcstruct
from funcstructs.prototypes.floatfuncs import UnitInterval, floatfunc


HalfOpenInterval = UnitInterval - {1}
f = floatfunc(lambda x: x*x, HalfOpenInterval)  # Float approx. to x**2

plt.figure()
plt.plot(*split(f, sort=True))
plt.title(r"Plot of $x^2$ on $[0, 1)$")
plt.show()

#' The plot, however, is not the 'true' graph of $f(x)$; it is the floating
#' point approximation. In particular, it is an approximation on the domain of
#' 16-bit floating point numbers between $0.0$ and $1.0$, of which there are
#' <%= len(HalfOpenInterval) %>.

#' Instead, we can view $f(x)$ as a discretely valued lookup table: given any
#' 16-bit floating point value $0\le x<1$, $f(x)$ returns the closest floating
#' point number to $x^2$.

#' f can be modeled using an associative array: the keys are 16-bit
#' floats, and the values of the keys are gotten from squaring the key.
#' Below is a sample of f represented as an associative array of (key,
#' value) pairs, printed below.

arr = np.ndarray([len(f)], dtype=object)
for i, v in enumerate(f.items()):
    arr[i] = v
print(arr)

#' We can also plot the values of f discretely.

plt.figure()
x, y = split(f)
plt.plot(x, y, 'ro', rasterized=True)
plt.title(r"Plot of $x^2$ as a discrete function of 16-bit floats.")
plt.show()

#' # Discrete Functions

#' When we repeatedly square a number $x\in [0, 1)$, it will tend toward $0$.
#' In a finite floating point approximation, this will happen in a finite
#' number of steps.

#' Since we already have our floating point map, we can simply use composition
#' to evaluate iterates of the map: the values of the array f become the keys
#' of its iterates, thus floating point multiplication and composition are
#' equivalent:

print(f * f == floatfunc(lambda x: (x*x)*(x*x), HalfOpenInterval))

#' Notice, however, that floating point multiplication is not associative. We
#' can verify this directly:

quartic = floatfunc(lambda x: x*x*x*x, HalfOpenInterval)
print(f * f == quartic)

#' # Endofunction Structures

#' In a sense, all meaningful aspects of a function's behavior under iteration
#' are determined by its graphical structure. Let $f:X\to X$ and $g:Y\to Y$.
#' These endofunctions are said to be conjugate if there exists an invertible
#' $\sigma: X \to Y$ such that $g = \sigma \circ f \circ \sigma^{-1}$.

#' Any functions for which this is true share the same graph structure. Below
#' is plotted another mapping of 16-bit floating point numbers on the unit
#' interval:

g = randconj(f)

plt.figure()
x, y = split(g)
plt.plot(x, y, 'o', markerfacecolor='orange', rasterized=True)
plt.title(r"Plot of a random conjugate of $x^2$ defined on 16-bit floats.")
plt.show()

#' Despite having no apparent relation with the familiar parabola, $f$ and $g$
#' have identical structure:

print(Funcstruct(f) == Funcstruct(g))

#' It may seem that such different functions sharing the same structure would
#' make this relationship useless. However, under iteration, we can much more
#' easily see the similarity: they both head toward a constant value in
#' precisely 16 iterations.


def treeiterates(func):
    """Return a list of all of f's iterates with tree-like structure."""
    f_orig = func
    lim = func.limitset
    while func.image != lim:
        yield func
        func *= f_orig
    yield func


def treeiterate_plot(func, show=True, legend_loc=0, title=None):
    """Plot all of f's tree-like iterates."""
    cm = plt.get_cmap('gist_rainbow')
    iterates = list(treeiterates(func))
    n = len(iterates)
    plt.figure()
    ax = plt.gca()
    ax.set_color_cycle([cm(1.*i/n) for i in range(n)])
    for i, f in enumerate(iterates):
        x, y = split(f)
        ax.plot(x, y, 'o', markerfacecolor=cm(1.*i/n), label=i, rasterized=1)
    ax.legend(numpoints=1, loc=legend_loc)
    if title is not None:
        plt.title(title)
    if show:
        plt.show()


treeiterate_plot(f, legend_loc="upper left", title=r"Iterates of $f(x)=x^2$")
treeiterate_plot(g, title=r"Iterates of a random conjugate of $f(x)=x^2$")

#' # Linear Operations

#' In fact, the "plot" of a function is actually a visualization of its
#' adjacency matrix: the zeros are the whitespace, and the ones are the plot
#' points. In this sense, composition of functions is multiplication of their
#' adjacency matrices.

#' The relationship between $f$ and $g$ is thus that their adjacency matrices
#' share the same eigenvalues.
