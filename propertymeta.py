import abc


def make_param_getter(key):
    def fget(self):
        return property(self.__params[key])
    return fget


class ParameterMeta(abc.ABCMeta):
    """Given a list of properties in the class definition statement, define a
    list of these properties, add each with a getter and setter from params,
    and add a list of these params."""

    def __new__(mcls, name, bases, dct):
        dct['__slots__'] = dct.pop('__parameters__', ())
        return super(ParameterMeta, mcls).__new__(mcls, name, bases, dct)


class A(object):
    __metaclass__ = ParameterMeta


a = A()
print(dir(a))


class A2(object):
    __metaclass__ = ParameterMeta

    @abc.abstractmethod
    def f(self):
        return 1


class A3(A2):
    __parameters__ = ['n', 'm']
    def f(self):
        return 2


a3 = A3()
print dir(a3)


class Enumerable(object):
    __metaclass__ = ParameterMeta

    @abc.abstractmethod
    def __new__(cls, **kwargs):
        self = super(Enumerable, cls).__new__(cls)
        for param, val in kwargs.items():
            setattr(self, param, make_param_getter(val))
        return self

    @abc.abstractmethod
    def __iter__(self):
        return
        yield


class Range(Enumerable):
    __parameters__ = ("start", "stop")

    def __new__(cls, start, stop=100):
        return super(Range, cls).__new__(cls, start=start, stop=stop)

    def __iter__(self):
        return iter(range(self.start, self.stop))


r = Range(20)
print dir(r)
r.start=20
print list(r)
