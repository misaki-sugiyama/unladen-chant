import pytest
from unladenchant.unladentaskbase import UnladenTaskBase

from types import SimpleNamespace as SNS

@pytest.fixture
def fixtureFlowCheck():
    aRecord = []
    class TaskBasic(UnladenTaskBase):
        def main(self, ns):
            aRecord.append('main' + str(getattr(ns, 'a', 0)))
            return True
    class TaskWithHooks(TaskBasic):
        @hook('preMain')
        def preMain1(self, ns):
            aRecord.append('pre' + str(getattr(ns, 'a', 0)))
            return True
        @hook('postMain')
        def postMain1(self, ns):
            aRecord.append('post' + str(getattr(ns, 'a', 0)))
            return True
    return SNS(aRecord=aRecord, TaskBasic=TaskBasic, TaskWithHooks=TaskWithHooks)

def test_did_nothing(fixtureFlowCheck):
    ns = fixtureFlowCheck
    assert ns.aRecord == []

def test_run(fixtureFlowCheck):
    ns = fixtureFlowCheck
    ns.TaskBasic().run()
    assert ns.aRecord == ['main0']

def test_run_twice(fixtureFlowCheck):
    ns = fixtureFlowCheck
    ns.TaskBasic().run()
    ns.TaskBasic().run()
    assert ns.aRecord == ['main0', 'main0']

def test_run_with_hook(fixtureFlowCheck):
    ns = fixtureFlowCheck
    ns.TaskWithHooks().run()
    assert ns.aRecord == ['pre0', 'main0', 'post0']

def test_run_with_hook_twice(fixtureFlowCheck):
    ns = fixtureFlowCheck
    ns.TaskWithHooks().run()
    ns.TaskWithHooks().run()
    assert ns.aRecord == ['pre0', 'main0', 'post0', 'pre0', 'main0', 'post0']

def test_run_with_hook_with_params(fixtureFlowCheck):
    ns = fixtureFlowCheck
    ns.TaskWithHooks().run(a=10)
    ns.TaskWithHooks().run(a=20)
    assert ns.aRecord == ['pre10', 'main10', 'post10', 'pre20', 'main20', 'post20']

def test_res_checker():
    aRecord = []
    def check1():
        aRecord.append('check1')
        return True
    def check2():
        return False
    class TaskRes(UnladenTaskBase):
        RESCHECK = (check1, )
        def main(self, ns):
            pass
    assert aRecord == ['check1']

def test_res_checker_fail():
    def check2():
        return False
    with pytest.raises(EnvironmentError):
        class TaskRes(UnladenTaskBase):
            RESCHECK = (check2, )
            def main(self, ns):
                pass
