from distutils.core import setup
from Cython.Build import cythonize

setup(ext_modules = cythonize(["*.py","PADS/IntegerPartitions.py","PADS.__init__.py"]))