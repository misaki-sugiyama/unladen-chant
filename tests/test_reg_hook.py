import pytest
from unladenchant.registryhook import RegistryHook, MetaMixinEnableHooks
from copy import copy

def checker_func_empty():
    pass

## Regarding register()

def test_will_register():
    objRH = RegistryHook()
    objRH.register(checker_func_empty)
    assert len(objRH.getFunctions()) == 1

def test_will_register_twice():
    objRH = RegistryHook()
    objRH.register(checker_func_empty)
    objRH.register(checker_func_empty)
    assert len(objRH.getFunctions()) == 1

def test_wont_register_noncallables():
    objRH = RegistryHook()
    with pytest.raises(TypeError):
        objRH.register(15)
    with pytest.raises(TypeError):
        objRH.register("abc")
    with pytest.raises(TypeError):
        objRH.register(False)

@pytest.fixture
def fixtureSimpleHook():
    listRecord = []
    def func1(a=0):
        listRecord.append(1+a)
        return 1+a
    def func2(a=0):
        listRecord.append(2+a)
        return 2+a
    def func3(a=0):
        listRecord.append(3+a)
        return 3+a
    objRH = RegistryHook()
    objRH.register(func1)
    objRH.register(func2)
    return objRH, listRecord, func1, func2, func3

## Invoked in correct order

def test_can_invoke(fixtureSimpleHook):
    objRH, listRecord, f1, f2, f3 = fixtureSimpleHook
    objRH.invoke()
    assert listRecord == [1, 2]

def test_can_invoke_with_param(fixtureSimpleHook):
    objRH, listRecord, f1, f2, f3 = fixtureSimpleHook
    objRH.invoke(10)
    assert listRecord == [11, 12]

def test_can_add_top(fixtureSimpleHook):
    objRH, listRecord, f1, f2, f3 = fixtureSimpleHook
    objRH.register(f3, atTop=True)
    objRH.invoke()
    assert listRecord == [3, 1, 2]

## Can deal with return value

def test_return_value(fixtureSimpleHook):
    objRH, listRecord, f1, f2, f3 = fixtureSimpleHook
    rslt = objRH.invoke(10)
    assert rslt[f1] == 11
    assert rslt[f2] == 12
    assert f3 not in rslt

## Regarding isRegistered()

def test_is_registered(fixtureSimpleHook):
    objRH, listRecord, f1, f2, f3 = fixtureSimpleHook
    assert objRH.isRegistered(f1)
    assert objRH.isRegistered(f2)
    assert not objRH.isRegistered(f3)

## Regarding getFunctions()

def test_can_get_functions(fixtureSimpleHook):
    objRH, listRecord, f1, f2, f3 = fixtureSimpleHook
    rslt = objRH.getFunctions()
    assert f1 in rslt
    assert f2 in rslt
    assert len(rslt) == 2

def test_cant_modify_function_list(fixtureSimpleHook):
    objRH, listRecord, f1, f2, f3 = fixtureSimpleHook
    rslt = objRH.getFunctions()
    # we don't actually mind what exception it raises, just fail fatally
    with pytest.raises(BaseException):
        rslt.append(123)

## Regarding getRegistrants()

def test_can_get_registrants(fixtureSimpleHook):
    objRH, listRecord, f1, f2, f3 = fixtureSimpleHook
    objRH.register(f2, checker_func_empty)
    objRH.register(f2, 'newreg')
    assert objRH.getRegistrants(f2) == {None, 'newreg', checker_func_empty}

def test_cant_get_non_registrants(fixtureSimpleHook):
    objRH, listRecord, f1, f2, f3 = fixtureSimpleHook
    with pytest.raises(TypeError):
        objRH.getRegistrants(f3)

def test_cant_modify_registrants(fixtureSimpleHook):
    objRH, listRecord, f1, f2, f3 = fixtureSimpleHook
    rslt = objRH.getRegistrants(f2)
    # we don't actually mind what exception it raises, just fail fatally
    with pytest.raises(BaseException):
        rslt.add(100)

## Regarding making a copy of registry hook object

@pytest.fixture
def fixtureCopyHook():
    def func1():
        pass
    def func2():
        pass
    objRH = RegistryHook()
    objRH.register(func1, '001')
    objRH.register(func2, '002')
    return objRH

def test_copied_hook_dont_affect_original(fixtureCopyHook):
    objRH = fixtureCopyHook
    def func3():
        pass
    objCopy = copy(objRH)
    objCopy.register(func3, '003')
    assert len(objRH.getFunctions()) == 2

def test_copied_hook_dont_affect_original_registrants(fixtureCopyHook):
    objRH = fixtureCopyHook
    def func3():
        pass
    objRH.register(func3, '003')
    objCopy = copy(objRH)
    objCopy.register(func3, 'new003')
    assert objRH.getRegistrants(func3) != objCopy.getRegistrants(func3)

def test_copied_functions_are_the_same(fixtureCopyHook):
    objRH = fixtureCopyHook
    objCopy = copy(objRH)
    assert objCopy.getFunctions() == objRH.getFunctions()
