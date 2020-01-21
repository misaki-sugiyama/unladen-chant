import pytest
pytestmark = pytest.mark.forked
from unladenchant.resourcecheck import RegistryResourceChecker as rrc

def checker_func_empty():
    pass

## Regarding register()

def test_will_register():
    rrc.register(checker_func_empty)

def test_will_register_twice():
    rrc.register(checker_func_empty)
    rrc.register(checker_func_empty)

def test_wont_register_noncallable():
    with pytest.raises(TypeError):
        rrc.register(15)
    with pytest.raises(TypeError):
        rrc.register("abc")
    with pytest.raises(TypeError):
        rrc.register(False)

@pytest.fixture
def fixtureCheckFunc():
    mTimes = {
        'resCheck1': 0,
        'resCheck2': 0,
        'resCheck3': 0,
    }
    def checker_func_1():
        mTimes['resCheck1'] += 1
        return True
    def checker_func_2():
        mTimes['resCheck2'] += 1
        return True
    def checker_func_3():
        mTimes['resCheck3'] += 1
        return False
    rrc.register(checker_func_1)
    rrc.register(checker_func_2)
    return mTimes, checker_func_1, checker_func_2, checker_func_3

## Regarding check()

def test_can_check(fixtureCheckFunc):
    mTimes, f1, f2, f3 = fixtureCheckFunc
    assert rrc.check(f1)
    assert mTimes['resCheck1'] == 1
    assert rrc.check(f2)
    assert mTimes['resCheck2'] == 1

def test_cant_check_unregistered(fixtureCheckFunc):
    mTimes, f1, f2, f3 = fixtureCheckFunc
    with pytest.raises(TypeError):
        rrc.check(f3)
    assert mTimes['resCheck3'] == 0

def test_can_repeat_check(fixtureCheckFunc):
    mTimes, f1, f2, f3 = fixtureCheckFunc
    rrc.register(f3)
    assert not rrc.check(f3)
    assert not rrc.check(f3)
    assert mTimes['resCheck3'] == 1
