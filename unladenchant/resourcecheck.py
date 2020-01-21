from .registryhook import RegistryHook

from functools import wraps

# This is designed to be used inside UnladenTask, not directly by user
class RegistryResourceChecker:
    # This will handle registration
    objRegistry = RegistryHook()
    # Record cached check results
    _mapResults = {}

    @classmethod
    def register(cls, fun, registrant=None):
        cls.objRegistry.register(fun, registrant=registrant)

    @classmethod
    def check(cls, fun):
        if fun in cls._mapResults:
            return cls._mapResults[fun]
        if not cls.objRegistry.isRegistered(fun):
            raise TypeError("This thing isn't registered as a checker")
        cls._mapResults[fun] = rslt = fun()
        return rslt

# The mixin metaclass to do resource check on class definition
class MetaMixinResourceChecker:
    def __new__(meta, name, bases, ns):
        cls = super().__new__(meta, name, bases, ns)
        # Register any resource checker defined
        for fun in getattr(cls, 'RESCHECK', ()):
            RegistryResourceChecker.register(fun, cls)
            if not RegistryResourceChecker.check(fun):
                raise EnvironmentError("Some resources needed by this program aren't there")
        return cls
