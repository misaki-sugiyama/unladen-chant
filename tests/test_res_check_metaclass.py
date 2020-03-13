import pytest
pytestmark = pytest.mark.forked
from unladenchant.resourcecheck import MetaMixinResourceChecker

class MetaClassTest(MetaMixinResourceChecker, type):
    pass

class BaseClass(metaclass=MetaClassTest):
    pass

## Testing pass and failure

def rescheckPassed():
    return True
def rescheckFailed():
    return False

def test_will_pass_if_res_okay():
    class NewClass(BaseClass):
        RESCHECK = (rescheckPassed,)

def test_will_fail_if_res_not_okay():
    with pytest.raises(EnvironmentError):
        class NewClass(BaseClass):
            RESCHECK = (rescheckFailed,)

def test_will_fail_if_res_not_okay_partially():
    with pytest.raises(EnvironmentError):
        class NewClass(BaseClass):
            RESCHECK = (rescheckFailed, rescheckPassed)

## Testing multiple checks

@pytest.fixture
def fixtureCheckCount():
    mTimes = {
        'resCheck2': 0,
        'resCheck': 0
    }
    def funCheckRes():
        mTimes['resCheck'] += 1
        return True
    def funCheckRes2():
        mTimes['resCheck2'] += 1
        return True
    return mTimes, funCheckRes, funCheckRes2

def test_did_run_once(fixtureCheckCount):
    mTimes, funCheckRes, funCheckRes2 = fixtureCheckCount
    class NewClass(BaseClass):
        RESCHECK = (funCheckRes, )
    assert mTimes == {'resCheck': 1, 'resCheck2': 0}

def test_did_run_once_only(fixtureCheckCount):
    mTimes, funCheckRes, funCheckRes2 = fixtureCheckCount
    class NewClass(BaseClass):
        RESCHECK = (funCheckRes, )
    class NewClass2(NewClass):
        RESCHECK = (funCheckRes, funCheckRes2)
    assert mTimes == {'resCheck': 1, 'resCheck2': 1}
