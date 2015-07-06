class DisabledMethod(TypeError):
    __module__ = "funcstructs"


def disabled_function_maker(name, message):
    """Create a classmethod with the given name raising the given message."""
    def disabledfunc(cls, *args, **kwargs):
        raise DisabledMethod(message.format(
            method=repr(name), cls=repr(cls.__name__)
        ))
    disabledfunc.__name__ = name
    disabledfunc.__doc__ = "Disabled method %s" % name
    return classmethod(disabledfunc)


def disable(*methods, **kwargs):
    """Class decorator to disable methods and raise a type error when
    they are called."""
    # None aliases to empty message. Also python3 syntax would be nice here...
    if 'message' in kwargs:
        message = kwargs.pop('message')
        if message is None:
            message = ""
    else:
        message = "{method} method is disabled for {cls} objects"
    if kwargs:
        raise TypeError("disable() got unexpected keyword argument %s" %
                        kwargs.popitem()[0])

    def disabling_decorator(cls):
        for method in methods:
            setattr(cls, method, disabled_function_maker(method, message))
        return cls

    return disabling_decorator
