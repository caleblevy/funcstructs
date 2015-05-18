import abc
import unittest

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


class ParametrizedABCTests(unittest.TestCase):

    def test_init(self):
        sr = StepRange(40)
        self.assertEqual(list(range(40, 100, 2)), list(sr))

    def test_unchangeable_attributes(self):
        sr = StepRange(40)
        sr_old = list(sr)
        with self.assertRaises(AttributeError):
            del sr._params
        with self.assertRaises(AttributeError):
            sr._params = {'start': 1, 'step': 4, 'stop': 40}
        with self.assertRaises(AttributeError):
            sr.aa4 = 20
        with self.assertRaises(AttributeError):
            del sr.start
        with self.assertRaises(AttributeError):
            sr.start = 10
        self.assertSequenceEqual(sr_old, list(sr))

    def test_mro(self):
        self.assertSequenceEqual(
            StepRange.mro(),
            [StepRange, Range, Enumerable, object]
        )

    def test_types(self):
        self.assertIsInstance(StepRange, ParameterMeta)
        self.assertIsInstance(ParameterMeta, type)
        self.assertTrue(issubclass(ParameterMeta, type))


if __name__ == '__main__':
    unittest.main()
