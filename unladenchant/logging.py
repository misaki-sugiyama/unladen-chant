from .unladentaskbase import MetaClassUnladenTask

import logging
import sys
import os
import os.path
import gzip
import shutil
import colorama
colorama.init()

class UnladenBaseFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        # Ignoring all arguments here
        super().__init__('%(asctime)s %(message)s', datefmt='%Y%m%d.%H%M%S')

class UnladenConsoleFormatter(UnladenBaseFormatter):
    def format(self, rec):
        if rec.levelno <= 10:
            sPre = colorama.Style.BRIGHT + colorama.Fore.BLACK + '[D]'
        elif rec.levelno <= 20:
            sPre = colorama.Style.BRIGHT + colorama.Fore.WHITE + '[I]'
        elif rec.levelno <= 30:
            sPre = colorama.Style.BRIGHT + colorama.Fore.YELLOW + '[W]'
        else:
            sPre = colorama.Style.BRIGHT + colorama.Fore.RED + '[E]'
        return '{} {}{}'.format(
            sPre,
            super().format(rec),
            colorama.Style.RESET_ALL
            )

class UnladenFileFormatter(UnladenBaseFormatter):
    def format(self, rec):
        if rec.levelno <= 10:
            sPre = '[D]'
        elif rec.levelno <= 20:
            sPre = '[I]'
        elif rec.levelno <= 30:
            sPre = '[W]'
        else:
            sPre = '[E]'
        return '{} {}'.format(
            sPre,
            super().format(rec)
            )

def doLogRotate(nameFile, nRotate=5, toCompress=True):
    if nRotate <= 0:
        return
    if toCompress:
        fmtBackup = '{}.{}.gz'.format(nameFile, '{:d}')
    else:
        fmtBackup = '{}.{}'.format(nameFile, '{:d}')
    # Delete last file
    if os.path.isfile(fmtBackup.format(nRotate)):
        os.unlink(fmtBackup.format(nRotate))
    # Rotate intermediate files
    for i in range(nRotate-1, 0, -1):
        if os.path.isfile(fmtBackup.format(i)):
            os.rename(fmtBackup.format(i), fmtBackup.format(i+1))
    # Rotate the main backup file
    if os.path.isfile(nameFile):
        if not toCompress:
            os.rename(nameFile, fmtBackup.format(1))
        else:
            with open(nameFile, 'rb') as fp, gzip.open(fmtBackup.format(1), 'wb') as fpw:
                shutil.copyfileobj(fp, fpw)

class MixinLogging(metaclass=MetaClassUnladenTask):
    ISABSTRACTCLASS = True
    @hook('args')
    def hook_args_logging(cls, parser):
        group = parser.add_argument_group('logging-related options')
        group.add_argument('--logfile', metavar='file')
        group.add_argument('--logrotate', type=int, metavar='int', default=5)
        group.add_argument('--logrotate-no-compress', action='store_true')

    def runWithNs(self, ns):
        ch = logging.StreamHandler(sys.stderr)
        ch.setLevel('INFO')
        ch.setFormatter(UnladenConsoleFormatter())
        self.logger.addHandler(ch)

        if ns.logfile:
            doLogRotate(ns.logfile, ns.logrotate, not ns.logrotate_no_compress)
            if os.path.dirname(ns.logfile):
                os.makedirs(os.path.dirname(ns.logfile), exist_ok=True)
            with open(ns.logfile, mode='w') as self.streamLog:
                fh = logging.StreamHandler(self.streamLog)
                fh.setLevel('DEBUG')
                fh.setFormatter(UnladenFileFormatter())
                self.logger.addHandler(fh)
                self.logger.debug('Logfile={} rotate={:d} no-compress={}'.format(ns.logfile, ns.logrotate, ns.logrotate_no_compress))
                return super().runWithNs(ns)
        else:
            return super().runWithNs(ns)
