import abc


def make_param_getter(key):
    def fget(self):
        return property(self.__params[key])
    return fget


def ro_property(name):
    def ro_property_decorator(c):
        setattr(c, name, property(lambda o: o._params[name]))
        return c
    return ro_property_decorator


class ParameterMeta(abc.ABCMeta):
    """Given a list of properties in the class definition statement, define a
    list of these properties, add each with a getter and setter from params,
    and add a list of these params."""

    def __new__(mcls, name, bases, dct):
        params = tuple(dct.pop('__parameters__', ()))
        dct['__slots__'] = params + ('_params',)
        cls = super(ParameterMeta, mcls).__new__(mcls, name, bases, dct)
        for param in params:
            cls = ro_property(param)(cls)
        return cls


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
    """Abstract base class"""
    __metaclass__ = ParameterMeta

    @abc.abstractmethod
    def __new__(cls, **kwargs):
        self = super(Enumerable, cls).__new__(cls)
        self._params = kwargs
        return self

    @abc.abstractmethod
    def __iter__(self):
        return
        yield


class Range(Enumerable):
    """Imitates range"""
    __parameters__ = ("start", "stop")

    def __new__(cls, start, stop=100):
        return super(Range, cls).__new__(cls, start=start, stop=stop)

    def __iter__(self):
        return iter(range(self.start, self.stop))


r = Range(20)
print dir(r)
print list(r)


class Ranger(Range):
    __parameters__ = ["step"]

    def __new__(cls, start, stop=100, step=2):
        return super(Range, cls).__new__(cls, start=start, stop=stop, step=step)

    def __iter__(self):
        return iter(range(self.start, self.stop, self.step))


rger = Ranger(40)
print dir(rger)
print list(rger)
