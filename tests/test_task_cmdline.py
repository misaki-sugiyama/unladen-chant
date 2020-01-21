import pytest
from unladenchant.unladentaskbase import UnladenTaskBase
from unladenchant.cmdline import MixinCommandLine

from types import SimpleNamespace as SNS

class UnladenWithCmdline(MixinCommandLine, UnladenTaskBase):
    ISABSTRACTCLASS = True

@pytest.fixture
def fixListNs():
    mNs = {}
    class ClassListNs(UnladenWithCmdline):
        def main(self, ns):
            mNs.update(vars(ns))
    class ClassParse(ClassListNs):
        def args(cls, parser):
            parser.add_argument('--option', '-o', type=int, default=15)
    return SNS(mNs=mNs, ClassListNs=ClassListNs, ClassParse=ClassParse)

def test_version(fixListNs):
    ns = fixListNs
    with pytest.raises(SystemExit) as e:
        ns.ClassListNs().runcmd(('--version',))
    assert e.value.code == 0

def test_help(fixListNs):
    ns = fixListNs
    with pytest.raises(SystemExit) as e:
        ns.ClassListNs().runcmd(('--help',))
    assert e.value.code == 0

def test_bad_args(fixListNs):
    ns = fixListNs
    with pytest.raises(SystemExit) as e:
        ns.ClassListNs().runcmd(('--nonexistent=10',))
    assert e.value.code == 2

def test_default_ns(fixListNs):
    ns = fixListNs
    ns.ClassListNs().runcmd()
    assert ns.mNs == {}

def test_declare_args(fixListNs):
    ns = fixListNs
    obj = ns.ClassParse()
    obj.runcmd(('--option=72',))
    assert ns.mNs['option'] == 72

def test_declare_args_through_hook(fixListNs):
    ns = fixListNs
    obj = ns.ClassParse()
    obj.runcmd(('--option=72',))
    assert ns.mNs['option'] == 72

def test_init_runcmd_notgiven(fixListNs):
    ns = fixListNs
    obj = ns.ClassParse(option=75)
    obj.runcmd()
    assert ns.mNs['option'] == 75

def test_init_runcmd_given(fixListNs):
    ns = fixListNs
    obj = ns.ClassParse(option=75)
    obj.runcmd(('--option=72',))
    assert ns.mNs['option'] == 72

def test_init_run_notgiven(fixListNs):
    ns = fixListNs
    obj = ns.ClassParse(option=75)
    obj.run()
    assert ns.mNs['option'] == 75

def test_init_run_given(fixListNs):
    ns = fixListNs
    obj = ns.ClassParse(option=75)
    obj.run(option=72)
    assert ns.mNs['option'] == 72
