from collections import defaultdict

def decoratorMustBeOverriden(fun):
    fun._mustBeOverriden = True
    return fun

def FactoryInstantiateForbidder(objClass):
    def __new__(cls, *args, **kwargs):
        if cls is objClass:
            raise TypeError("{} is an abstract class, cannot be instantiated".format(cls.__name__))
        return super(objClass, cls).__new__(cls)
    return __new__

# The mixin metaclass to enforce some methods to be overriden
class MetaMixinOverrideEnforcer:
    @classmethod
    def __prepare__(meta, name, bases, **kwargs):
        return {
            **(super().__prepare__(name, bases, **kwargs)),
            'mustBeOverriden': decoratorMustBeOverriden
            }

    def __new__(meta, name, bases, ns):
        cls = super().__new__(meta, name, bases, ns)
        if 'ISABSTRACTCLASS' in cls.__dict__:
            cls.__new__ = staticmethod(FactoryInstantiateForbidder(cls))
            return cls
        for nameFun in dir(cls):
            if getattr(getattr(cls, nameFun), '_mustBeOverriden', False):
                raise NotImplementedError("{}.{}() is not overriden".format(cls.__name__, nameFun))
        return cls
