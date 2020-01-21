from .resourcecheck import MetaMixinResourceChecker
from .overrideenforcer import MetaMixinOverrideEnforcer
from .registryhook import MetaMixinEnableHooks

from types import SimpleNamespace as SNS
import logging

class MetaClassUnladenTask(MetaMixinOverrideEnforcer, MetaMixinEnableHooks, MetaMixinResourceChecker, type):
    pass

class UnladenTaskBase(metaclass=MetaClassUnladenTask):
    ISABSTRACTCLASS = True
    # Placeholders, for the actual task to declare
    @mustBeOverriden
    def main(self, ns): # pragma: no cover
        pass

    def __init__(self, *args, **kwargs):
        # Get an unique default logger for this task
        self.logger = logging.getLogger(str(id(self)))
        self.logger.propagate = False
        self.logger.setLevel(logging.DEBUG)
        super().__init__()

    # Interfaces to run
    def invokeMain(self, ns):
        return self.main(ns)
    def runWithNs(self, ns):
        self.invokeHook('preMain', ns)
        rslt = self.invokeMain(ns)
        self.invokeHook('postMain', ns)
        return rslt
    def run(self, **kwargs):
        return self.runWithNs(SNS(**kwargs))
