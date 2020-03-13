import pytest
from unladenchant.unladentaskbase import UnladenTaskBase
from unladenchant.cmdline import MixinCommandLine
from unladenchant.logging import MixinLogging

from types import SimpleNamespace as SNS
import re
import os
import os.path
import gzip

class UnladenWithLogging(MixinLogging, MixinCommandLine, UnladenTaskBase):
    ISABSTRACTCLASS = True

@pytest.fixture(params=('/aaa/ログ .log',))
def fixLogger(fs, request):
    class ClassLog(UnladenWithLogging):
        def args(cls, parser):
            parser.add_argument('--num', type=int, default=0)
        def main(self, ns):
            self.logger.debug('maindebug.{:d}'.format(ns.num))
    return SNS(fs=fs, ClassLog=ClassLog, fname=request.param)

def test_write_log_fixed(fixLogger):
    ns = fixLogger
    ns.ClassLog().runcmd(('--logfile={}'.format(ns.fname),))
    with open(ns.fname) as fp:
        strLog = fp.read()
        assert re.search(r'\[D\] [^ ]+ Invoked with parameters', strLog)
        assert re.search(r'.num.: 0', strLog)
        assert re.search(r'\[D\] [^ ]+ Running Pre Hook', strLog)
        assert re.search(r'Main Script', strLog)
        assert re.search(r'\[D\] [^ ]+ Running Post Hook', strLog)

def test_write_log(fixLogger):
    ns = fixLogger
    ns.ClassLog().runcmd(('--logfile={}'.format(ns.fname),))
    with open(ns.fname) as fp:
        strLog = fp.read()
        assert re.search(r'\[D\] [^ ]+ maindebug.0', strLog)
        assert re.search(r'\[D\] [^ ]+ Logfile={}'.format(ns.fname), strLog)

def test_log_invoke_subtask(fs):
    class ClassLogging(UnladenWithLogging):
        def args(cls, parser):
            parser.add_argument('--num', type=int, default=0)
        def main(self, ns):
            return True
    class ClassLogging2(UnladenWithLogging):
        def main(self, ns):
            return self.invokeSubTask(ClassLogging(), num=23)
    ClassLogging2().runcmd(('--logfile=/a.log',))
    with open('/a.log') as fp:
        strLog = fp.read()
        assert re.search('.num.: 23', strLog)
        assert re.search(r'\[D\] [^ ]+ .*subtask .*ClassLogging.* with', strLog)
        assert re.search(r'\[D\] [^ ]+ Subtask .*ClassLogging.* returned True', strLog)

def test_write_log_stream(fs):
    class ClassLogStream(UnladenWithLogging):
        def main(self, ns):
            self.streamLog.write('write stream\n')
    ClassLogStream().runcmd(('--logfile=/a.log',))
    with open('/a.log') as fp:
        strLog = fp.read()
        assert re.search('write stream', strLog)

def test_log_various_level(fs, capsys):
    class ClassLog(UnladenWithLogging):
        def main(self, ns):
            self.logger.info('info1')
            self.logger.warning('warn1')
            self.logger.error('error1')
    ClassLog().runcmd(('--logfile=a.log',))
    strStderr = capsys.readouterr().err
    with open('a.log') as fp:
        strLog = fp.read()
        assert re.search(r'\[I\] [^ ]+ info1', strLog)
        assert re.search(r'\[W\] [^ ]+ warn1', strLog)
        assert re.search(r'\[E\] [^ ]+ error1', strLog)
    assert re.search(r'\[I\] [^ ]+ info1', strStderr)
    assert re.search(r'\[W\] [^ ]+ warn1', strStderr)
    assert re.search(r'\[E\] [^ ]+ error1', strStderr)

@pytest.mark.parametrize('nRotate', (0, 3))
@pytest.mark.parametrize('repeat', (5,))
def test_logrotate_nocompress(fixLogger, repeat, nRotate):
    ns = fixLogger
    for i in range(repeat):
        ns.ClassLog().runcmd((
            '--logrotate={:d}'.format(nRotate),
            '--logrotate-no-compress',
            '--logfile={}'.format(ns.fname),
            '--num={}'.format(i+1)
        ))
    with open(ns.fname) as fp:
        strLog = fp.read()
        assert re.search('maindebug.{:d}'.format(repeat), strLog)
    for i in range(repeat-1):
        fnameThis = '{}.{:d}'.format(ns.fname, i+1)
        numThis = repeat - (i+1)
        if i+1 > nRotate:
            assert not os.path.isfile(fnameThis)
            continue
        with open(fnameThis) as fp:
            strLog = fp.read()
            assert re.search('maindebug.{:d}'.format(numThis), strLog)

@pytest.mark.parametrize('nRotate', (-15, 0, 3))
@pytest.mark.parametrize('repeat', (1, 4, 5))
def test_logrotate_compress(fixLogger, repeat, nRotate):
    ns = fixLogger
    for i in range(repeat):
        ns.ClassLog().runcmd((
            '--logrotate={:d}'.format(nRotate),
            '--logfile={}'.format(ns.fname),
            '--num={}'.format(i+1)
        ))
    with open(ns.fname) as fp:
        strLog = fp.read()
        assert re.search('maindebug.{:d}'.format(repeat), strLog)
    for i in range(repeat-1):
        fnameThis = '{}.{:d}.gz'.format(ns.fname, i+1)
        numThis = repeat - (i+1)
        if i+1 > nRotate:
            assert not os.path.isfile(fnameThis)
            continue
        with gzip.open(fnameThis, 'rt') as fp:
            strLog = fp.read()
            assert re.search('maindebug.{:d}'.format(numThis), strLog)
