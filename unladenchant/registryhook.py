from collections import defaultdict
from copy import copy, deepcopy
from itertools import chain

# A list of functions to be executed when invoked
class RegistryHook:
    def __init__(self):
        self._aFunc = []
        # which registrant registered these functions
        self._mRegister = defaultdict(set)

    # TODO: before/after specs
    def register(self, fun, registrant=None, atTop=False):
        if not callable(fun):
            raise TypeError("Cannot register non-callables as hook functions")
        if fun not in self._mRegister:
            if atTop:
                self._aFunc.insert(0, fun)
            else:
                self._aFunc.append(fun)
        self._mRegister[fun].add(registrant)

    def invoke(self, *args, **kwargs):
        return {
            func: func(*args, **kwargs) for func in self._aFunc
        }

    def __copy__(self):
        objNew = RegistryHook()
        objNew._aFunc = copy(self._aFunc)
        objNew._mRegister = deepcopy(self._mRegister)
        return objNew

    # Inspectors

    def getRegistrants(self, fun):
        if fun not in self._mRegister:
            raise TypeError("This thing isn't registered as a hook function")
        return frozenset(self._mRegister[fun])

    def isRegistered(self, fun):
        return fun in self._mRegister

    def getFunctions(self):
        return tuple(self._aFunc)

# The method to get a hook copy for inspection
class GetHook(object):
    def __get__(self, obj, cls):
        def getHookInstance(nameHook, *args, **kwargs):
            return copy(obj._mapClassHook[nameHook])
        def getHookClass(nameHook, *args, **kwargs):
            return copy(cls._mapClassHook[nameHook])
        if obj is None:
            return getHookClass
        else:
            return getHookInstance

# The method to run a hook
class InvokeHook(object):
    def __get__(self, obj, cls):
        def invokeHookInstance(nameHook, *args, **kwargs):
            objHook = obj._mapClassHook[nameHook]
            return objHook.invoke(obj, *args, **kwargs)
        def invokeHookClass(nameHook, *args, **kwargs):
            objHook = cls._mapClassHook[nameHook]
            return objHook.invoke(cls, *args, **kwargs)
        if obj is None:
            return invokeHookClass
        else:
            return invokeHookInstance

def factoryDecoratorHook(registrant, target):
    def decoratorHook(name, *args, **kwargs):
        def decoratorInner(func):
            target.append((name, func, args, {**kwargs, 'registrant': registrant}))
            return func
        return decoratorInner
    return decoratorHook

# The mixin metaclass to add hooking capability to UnladenTask class
class MetaMixinEnableHooks:
    @classmethod
    def __prepare__(meta, name, bases, **kwargs):
        listRegistrationOfHooks = list(chain.from_iterable(
            getattr(b, '_listRegistrationOfHooks', []) for b in bases
        ))
        return {
            **(super().__prepare__(name, bases, **kwargs)),
            '_listRegistrationOfHooks': listRegistrationOfHooks,
            'hook': factoryDecoratorHook(name, listRegistrationOfHooks)
            }

    def __new__(meta, name, bases, ns):
        cls = super().__new__(meta, name, bases, ns)
        cls.invokeHook = InvokeHook()
        cls.getHook = GetHook()
        cls._mapClassHook = defaultdict(RegistryHook)
        for entry in cls._listRegistrationOfHooks:
            cls._mapClassHook[entry[0]].register(entry[1], *entry[2], **entry[3])
        cls.invokeHook('onClassCreation')
        return cls
