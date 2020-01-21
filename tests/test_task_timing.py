import pytest
from unladenchant.unladentaskbase import UnladenTaskBase
from unladenchant.cmdline import MixinCommandLine
from unladenchant.logging import MixinLogging
from unladenchant.timing import MixinTiming, getTimeString

from types import SimpleNamespace as SNS
from datetime import timedelta
import re

class UnladenWithTiming(MixinLogging, MixinTiming, MixinCommandLine, UnladenTaskBase):
    ISABSTRACTCLASS = True

@pytest.fixture
def fixTimer(fs, request):
    class ClassTimer(UnladenWithTiming):
        def main(self, ns):
            pass
    class ClassTimer2(UnladenWithTiming):
        def main(self, ns):
            ClassTimer().runcmd(('--colorful-header',))
    return SNS(fs=fs, ClassTimer=ClassTimer, ClassTimer2=ClassTimer2)

def test_timing_log(fixTimer):
    ns = fixTimer
    ns.ClassTimer().runcmd(('--logfile=a.log',))
    with open('a.log') as fp:
        strLog = fp.read()
        assert re.search(r'\(1\) Begin ClassTimer', strLog)
        assert re.search(r'\(1\) End ClassTimer Elapsed .*s', strLog)

def test_timing_header(fixTimer, capsys):
    ns = fixTimer
    ns.ClassTimer().runcmd(('--colorful-header',))
    strStderr = capsys.readouterr().err
    assert re.search(r'======.* \(1\).* Begin ClassTimer .*======', strStderr)
    assert re.search(r'======.* \(1\).* End ClassTimer .*\[[0-9mh]+s\] .*======', strStderr)

def test_timing_header_nested(fixTimer, capsys):
    ns = fixTimer
    ns.ClassTimer2().runcmd(('--colorful-header',))
    strStderr = capsys.readouterr().err
    assert re.search(r'======.* \(1\).* Begin ClassTimer2 .*======', strStderr)
    assert re.search(r'======.* \(1\).* End ClassTimer2 .*\[[0-9mh]+s\] .*======', strStderr)
    assert re.search(r'======.* \(2\).* Begin ClassTimer .*======', strStderr)
    assert re.search(r'======.* \(2\).* End ClassTimer .*\[[0-9mh]+s\] .*======', strStderr)

## Regarding getTimeString

@pytest.mark.parametrize('sec,ans', (
    (0, '0s'), (1, '1s'), (59, '59s'), (60, '1m0s'), (150, '2m30s'),
    (3599, '59m59s'), (3600, '1h0m0s'), (8888, '2h28m8s')
))
def test_time_string(sec, ans):
    objDelta = timedelta(seconds=sec)
    assert getTimeString(objDelta) == ans
