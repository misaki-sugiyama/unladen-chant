import pytest
from unladenchant.registryhook import MetaMixinEnableHooks

from types import SimpleNamespace as SNS

class MetaClassTest(MetaMixinEnableHooks, type):
    pass

class BaseClass(metaclass=MetaClassTest):
    pass

@pytest.fixture
def fixClassHook():
    aRecord = []
    class C1(BaseClass):
        @hook('hook1')
        def f2(self, a=0):
            aRecord.append(self)
            aRecord.append(a+2)
            return a+2
    class C2(BaseClass):
        @hook('hook1')
        def f3(self, a=0):
            aRecord.append(self)
            aRecord.append(a+3)
            return a+3
    class C1a(C2, C1):
        @hook('hook1')
        def f1(self, a=0):
            aRecord.append(self)
            aRecord.append(a+1)
            return a+1
    class C1b(C1a):
        @hook('hook1', atTop=True)
        def f6(self, a=0):
            aRecord.append(self)
            aRecord.append(a+6)
            return a+6
    def f0(self, a=0):
        aRecord.append(aRecord+0)
    return SNS(aRecord=aRecord, C1=C1, C2=C2, C1a=C1a, C1b=C1b, f0=f0)

@pytest.fixture
def fixInstHook(fixClassHook):
    ns = fixClassHook
    ns.o1 = ns.C1()
    ns.o2 = ns.C2()
    ns.o1a = ns.C1a()
    ns.o1b = ns.C1b()
    return ns

## invokeHook

def test_invoke_empty():
    obj = BaseClass()
    assert obj.invokeHook('nonexistent') == {}

def test_invoke_instance(fixInstHook):
    ns = fixInstHook
    ns.o1.invokeHook('hook1')
    assert ns.aRecord == [ns.o1, 2]

def test_invoke_classmethod(fixClassHook):
    ns = fixClassHook
    ns.C1.invokeHook('hook1')
    assert ns.aRecord == [ns.C1, 2]

## getHook

def test_getHook_instance_immutable(fixInstHook):
    ns = fixInstHook
    objHook = ns.o1.getHook('hook1')
    objHook.register(ns.f0)
    ns.o1.invokeHook('hook1')
    assert ns.aRecord == [ns.o1, 2]

def test_getHook_classmethod_immutable(fixClassHook):
    ns = fixClassHook
    objHook = ns.C1.getHook('hook1')
    objHook.register(ns.f0)
    ns.C1.invokeHook('hook1')
    assert ns.aRecord == [ns.C1, 2]

## invokeHook - multiclass

def test_invoke_subclass_instance(fixInstHook):
    ns = fixInstHook
    ns.o1a.invokeHook('hook1')
    assert ns.aRecord == [ns.o1a, 3, ns.o1a, 2, ns.o1a, 1]

def test_invoke_subclass_classmethod(fixClassHook):
    ns = fixClassHook
    ns.C1a.invokeHook('hook1')
    assert ns.aRecord == [ns.C1a, 3, ns.C1a, 2, ns.C1a, 1]

def test_invoke_subclass_atTop(fixInstHook):
    ns = fixInstHook
    ns.o1b.invokeHook('hook1')
    assert ns.aRecord == [ns.o1b, 6, ns.o1b, 3, ns.o1b, 2, ns.o1b, 1]

## Return Value

def test_invoke_return_instance(fixInstHook):
    ns = fixInstHook
    rslt = ns.o1a.invokeHook('hook1')
    assert rslt[ns.C2.f3] == 3
    assert rslt[ns.C1.f2] == 2
    assert rslt[ns.C1a.f1] == 1

def test_invoke_return_classmethod(fixClassHook):
    ns = fixClassHook
    rslt = ns.C1a.invokeHook('hook1')
    assert rslt[ns.C2.f3] == 3
    assert rslt[ns.C1.f2] == 2
    assert rslt[ns.C1a.f1] == 1

## Special Hook: onClassCreation

def test_special_hook_onClassCreation(fixInstHook):
    ns = fixInstHook
    class C1aCreate(ns.C1a):
        @hook('onClassCreation')
        def fCreate(self):
            self.invokeHook('hook1')
    obj3 = C1aCreate()
    assert ns.aRecord == [C1aCreate, 3, C1aCreate, 2, C1aCreate, 1]
