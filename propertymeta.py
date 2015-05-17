

def make_param_getter(key):
    def fget(self):
        return self.__params[key]
    return fget


class ParameterMeta(type):
    """Given a list of properties in the class definition statement, define a
    list of these properties, add each with a getter and setter from params,
    and add a list of these params."""

    def __new__(mcls, name, bases, dct):
        params = dct.pop('__parameters__', ())
        for param in params:
            dct[param] = property(make_param_getter(param))
        dct['__slots__'] = '__params'
        return super(ParameterMeta, mcls).__new__(mcls, name, bases, dct)


class A(object, metaclass=ParameterMeta):
    __metaclass__ = ParameterMeta
    __parameters__ = ["n", "m", "k"]
    def __init__(self):
        self.__params = {}
        self.__params['n'] = 1
        self.__params['m'] = 2
        self.__params['k'] = 3


a = A()
print(a)
print(dir(a))

class B(A):
    __metaclass__ = type
    __slots__ = 'l'
    def __init__(self):
        self.__params = {}
        self.__params['l'] = 4


b = B()
print(dir(b))
print(b)
print(a.m)