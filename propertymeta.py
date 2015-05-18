import abc
from six import with_metaclass


def ro_parameter(name):
    """Add a getter for the parameter of the given name to cls"""
    def ro_parameter_decorator(cls):
        setattr(cls, name, property(lambda self: self._params[name]))
        return cls
    return ro_parameter_decorator


class ParameterMeta(abc.ABCMeta):
    """Given a list of properties in the class definition statement, define a
    list of these properties, add each with a getter and setter from params,
    and add a list of these params."""

    def __new__(mcls, name, bases, dct):
        params = tuple(dct.pop('__parameters__', ()))
        dct['__slots__'] = params
        if not (bases and all(isinstance(base, mcls) for base in bases)):
            dct['__slots__'] += ('_params', )
        cls = super(ParameterMeta, mcls).__new__(mcls, name, bases, dct)
        for param in params:
            cls = ro_parameter(param)(cls)
        return cls


class Enumerable(with_metaclass(ParameterMeta, object)):
    """Abstract base class"""

    @abc.abstractmethod
    def __new__(cls, **kwargs):
        self = super(Enumerable, cls).__new__(cls)
        self._params = kwargs
        return self

    @abc.abstractmethod
    def __iter__(self):
        return
        yield

    def __setattr__(self, name, val):
        if name == "_params" and hasattr(self, "_params"):
            raise AttributeError("can't set attribute")
        else:
            super(Enumerable, self).__setattr__(name, val)

    def __delattr__(self, name):
        if name == "_params" and hasattr(self, "_params"):
            raise AttributeError("can't delete attribute")
        else:
            super(Enumerable, self).__delattr__(name)


class Range(Enumerable):
    """Imitates range"""
    __parameters__ = ("start", "stop")

    def __new__(cls, start, stop=100):
        return super(Range, cls).__new__(cls, start=start, stop=stop)

    def __iter__(self):
        return iter(range(self.start, self.stop))


class StepRange(Range):
    __parameters__ = ["step"]

    def __new__(cls, start, stop=100, step=2):
        return super(Range, cls).__new__(cls, start=start, stop=stop,
                                         step=step)

    def __iter__(self):
        return iter(range(self.start, self.stop, self.step))


sr = StepRange(40)
print(list(sr))
print(dir(sr))
print(StepRange.__mro__)
print(type(StepRange))
print(type(StepRange) is ParameterMeta)
try:
    sr._params = 40
except:
    pass
del sr._params
del sr.abc
