#!/usr/bin/env python3

from unladenchant.unladentaskbase import UnladenTaskBase
from unladenchant.cmdline import MixinCommandLine
from unladenchant.logging import MixinLogging
from unladenchant.timing import MixinTiming
from unladenchant.utils import PBar
import sys

class UnladenWithLogging(MixinLogging, MixinTiming, MixinCommandLine, UnladenTaskBase):
    ISABSTRACTCLASS = True

class Task1(UnladenWithLogging):
    def main(self, ns):
        import time
        with PBar((3,4,5,6,7), unit='b') as pb:
            for i in pb:
                time.sleep(0.6)
        print(vars(ns))

Task1().runcmd(sys.argv[1:])
