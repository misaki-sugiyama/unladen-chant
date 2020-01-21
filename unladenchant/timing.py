from .unladentaskbase import MetaClassUnladenTask

import sys
from datetime import datetime
import colorama
colorama.init()

# Global variable to record nest level for printColorfulHeader
levelNestedHeader = 1

def getTimeString(timeElapsed):
    h, r = divmod(timeElapsed.total_seconds(), 3600)
    m, s = divmod(r, 60)
    if h == 0 and m == 0:
        return '{:d}s'.format(int(s))
    elif h == 0:
        return '{:d}m{:d}s'.format(int(m), int(s))
    else:
        return '{:d}h{:d}m{:d}s'.format(int(h), int(m), int(s))


class MixinTiming(metaclass=MetaClassUnladenTask):
    ISABSTRACTCLASS = True
    @hook('args')
    def hook_args_timing(cls, parser):
        group = parser.add_argument_group('timing-related options')
        group.add_argument('--colorful-header', action='store_true')

    def runWithNs(self, ns):
        self.logTaskBegin(ns)
        try:
            return super().runWithNs(ns)
        finally:
            self.logTaskEnd(ns)

    def logTaskBegin(self, ns):
        global levelNestedHeader
        titleTask = self.getName(ns)
        self.timeBegin = datetime.now()
        self.logger.debug('({:d}) Begin {}'.format(levelNestedHeader, titleTask))
        if ns.colorful_header:
            sys.stderr.write('{} ====== ({:d}) {}{:%Y%m%d.%H%M%S} Begin {} {}======{}\n'.format(
                colorama.Style.BRIGHT + colorama.Fore.GREEN,
                levelNestedHeader,
                colorama.Style.BRIGHT + colorama.Fore.MAGENTA,
                self.timeBegin,
                titleTask,
                colorama.Style.BRIGHT + colorama.Fore.GREEN,
                colorama.Style.RESET_ALL
            ))
        levelNestedHeader += 1

    def getElapsedTimeDelta(self):
        return datetime.now() - self.timeBegin

    def logTaskEnd(self, ns):
        global levelNestedHeader
        levelNestedHeader -= 1
        titleTask = self.getName(ns)
        strElapsed = getTimeString(self.getElapsedTimeDelta())
        self.logger.debug('({:d}) End {} Elapsed {}'.format(levelNestedHeader, titleTask, strElapsed))
        if ns.colorful_header:
            # TODO: different separator for different level
            sys.stderr.write('{} ====== ({:d}) {}{:%Y%m%d.%H%M%S} End {} {}[{}] ======{}\n'.format(
                colorama.Style.BRIGHT + colorama.Fore.GREEN,
                levelNestedHeader,
                colorama.Style.BRIGHT + colorama.Fore.MAGENTA,
                datetime.now(),
                titleTask,
                colorama.Style.BRIGHT + colorama.Fore.GREEN,
                strElapsed,
                colorama.Style.RESET_ALL
            ))
