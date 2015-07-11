"""Frozen dictionary.

Caleb Levy, 2015.
"""

import functools
from six import with_metaclass


def _frozendict_method(name, map_get):
    dict_method = getattr(dict, name)

    def method(self, *args, **kwargs):
        return dict_method(map_get(self), *args, **kwargs)
    method.__name__ = name
    method.__doc__ = dict_method.__doc__
    return method


def _FrozendictMeta(name, bases, dct):
    """Modify a frozendict to remove member descriptors."""
    dct['__slots__'] = '_mapping'
    cls = type(name, bases, dct)
    _mapping = cls._mapping
    map_set = _mapping.__set__
    map_get = _mapping.__get__

    del cls._mapping
    del cls.__slots__

    def __new__(*args, **kwargs):
        self = super(cls, args[0]).__new__(args[0])
        map_set(self, dict(*args[1:], **kwargs))
        return self
    cls.__new__ = staticmethod(__new__)

    dict_methods = [
        '__contains__',
        '__eq__',
        '__getitem__',
        '__iter__',
        '__len__',
        '__ne__',
        '__sizeof__',
        'get',
        'items',
        'keys',
        'values'
    ]

    if hasattr(dict, 'iterkeys'):
        dict_methods.extend([
            'viewkeys',
            'viewvalues',
            'viewitems',
            'iterkeys',
            'itervalues',
            'iteritems'
        ])

    for method in dict_methods:
        setattr(cls, method, _frozendict_method(method, map_get))

    # Define here to make all base methods independant

    def copy(self):
        """Return a dictionary copy of self."""
        return dict.copy(map_get(self))

    def __hash__(self):
        return hash(frozenset(map_get(self).items()))

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, map_get(self))

    __repr__.__doc__ = dict.__repr__.__doc__

    cls.copy = copy
    cls.__hash__ = __hash__
    cls.__repr__ = __repr__

    def fromkeys(*args, **kwargs):
        return args[0](dict.fromkeys(*args[1:], **kwargs))

    fromkeys.__doc__ = dict.fromkeys.__doc__
    cls.fromkeys = classmethod(fromkeys)

    return cls


class frozendict(object, metaclass=_FrozendictMeta):
    """An immutable, hashable dictionary."""
    # __metaclass__ = _FrozendictMeta


a = frozendict({1: 1, 2: 2, 'a': 3})
print(a)
print(repr(a))
b = dict(a)
print(b)
print(b == a)
print(dir(a))
db = dir(b)
for method in ['__setitem__', '__delitem__', 'clear', 'pop',
               'popitem', 'update', 'setdefault']:
    db.remove(method)
for attr in dir(a):
    if attr not in db:
        print(attr)
print(db)
print(type(frozendict))
