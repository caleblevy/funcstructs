import sys
import os

try:
    sys.path.append(os.path.join(os.getcwd(), 'PADS'))
    del sys, os
except Exception as e:
    raise e

from .structures.__init__ import *
from .bases.__init__ import frozendict, Enumerable
