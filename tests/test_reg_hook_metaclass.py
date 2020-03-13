import pytest
from unladenchant.registryhook import MetaMixinEnableHooks

from types import SimpleNamespace as SNS

class MetaClassTest(MetaMixinEnableHooks, type):
    pass

class BaseClass(metaclass=MetaClassTest):
    pass

## invokeHook

@pytest.fixture
def fixSimpleHook():
    aRecord = []
    class C(BaseClass):
        @hook('hook1')
        def f(self):
            aRecord.append(self)
    def f0(self, a=0):
        aRecord.append(0)
    return SNS(aRecord=aRecord, C=C, o=C(), f0=f0)

def test_invoke_empty():
    obj = BaseClass()
    assert obj.invokeHook('nonexistent') == {}

def test_invoke_instance(fixSimpleHook):
    ns = fixSimpleHook
    ns.o.invokeHook('hook1')
    assert ns.aRecord == [ns.o]

def test_invoke_classmethod(fixSimpleHook):
    ns = fixSimpleHook
    ns.C.invokeHook('hook1')
    assert ns.aRecord == [ns.C]

## getHook

def test_getHook_instance_immutable(fixSimpleHook):
    ns = fixSimpleHook
    objHook = ns.o.getHook('hook1')
    objHook.register(ns.f0)
    ns.o.invokeHook('hook1')
    assert ns.aRecord == [ns.o]

def test_getHook_classmethod_immutable(fixSimpleHook):
    ns = fixSimpleHook
    objHook = ns.C.getHook('hook1')
    objHook.register(ns.f0)
    ns.C.invokeHook('hook1')
    assert ns.aRecord == [ns.C]

## Return value

@pytest.fixture
def fixReturnHook():
    class C(BaseClass):
        @hook('hook1')
        def f(self):
            return self
        @hook('hook1')
        def f2(self):
            return "f2"
    return SNS(C=C, o=C())

def test_invoke_return_instance(fixReturnHook):
    ns = fixReturnHook
    rslt = ns.o.invokeHook('hook1')
    assert rslt[ns.C.f] == ns.o
    assert rslt[ns.C.f2] == "f2"

def test_invoke_return_classmethod(fixReturnHook):
    ns = fixReturnHook
    rslt = ns.C.invokeHook('hook1')
    assert rslt[ns.C.f] == ns.C
    assert rslt[ns.C.f2] == "f2"

## invokeHook - multiclass

@pytest.fixture
def fixClassHook():
    aRecord = []
    class C1(BaseClass):
        @hook('hook1')
        def f2(self, a=0):
            aRecord.append(self)
            aRecord.append(a+2)
    class C2(BaseClass):
        @hook('hook1')
        def f3(self, a=0):
            aRecord.append(self)
            aRecord.append(a+3)
    class C1a(C2, C1):
        @hook('hook1')
        def f1(self, a=0):
            aRecord.append(self)
            aRecord.append(a+1)
    class C1b(C1a):
        @hook('hook1', atTop=True)
        def f6(self, a=0):
            aRecord.append(self)
            aRecord.append(a+6)
    return SNS(aRecord=aRecord, C1=C1, C2=C2, C1a=C1a, C1b=C1b)

@pytest.fixture
def fixInstHook(fixClassHook):
    ns = fixClassHook
    ns.o1 = ns.C1()
    ns.o2 = ns.C2()
    ns.o1a = ns.C1a()
    ns.o1b = ns.C1b()
    return ns

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

## Special Hook: onClassCreation

def test_special_hook_onClassCreation(fixInstHook):
    ns = fixInstHook
    class C1aCreate(ns.C1a):
        @hook('onClassCreation')
        def fCreate(self):
            self.invokeHook('hook1')
    obj3 = C1aCreate()
    assert ns.aRecord == [C1aCreate, 3, C1aCreate, 2, C1aCreate, 1]
