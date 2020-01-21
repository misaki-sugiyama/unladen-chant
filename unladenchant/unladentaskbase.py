from .resourcecheck import MetaMixinResourceChecker
from .overrideenforcer import MetaMixinOverrideEnforcer
from .registryhook import MetaMixinEnableHooks

from types import SimpleNamespace as SNS
import logging
from pprint import pformat

class MetaClassUnladenTask(MetaMixinOverrideEnforcer, MetaMixinEnableHooks, MetaMixinResourceChecker, type):
    pass

class UnladenTaskBase(metaclass=MetaClassUnladenTask):
    ISABSTRACTCLASS = True
    # Placeholders, for the actual task to declare
    @mustBeOverriden
    def main(self, ns): # pragma: no cover
        pass

    def getName(self, ns):
        return self.__class__.__name__

    def __init__(self, *args, **kwargs):
        # Get an unique default logger for this task
        self.logger = logging.getLogger(str(id(self)))
        self.logger.propagate = False
        self.logger.setLevel(logging.DEBUG)
        super().__init__()

    # Invoke other task with some log
    def invokeSubTask(self, objTask, **kwargs):
        self.logger.debug("Invoking subtask {} with parameters:\n{}".format(
            str(objTask),
            pformat(kwargs)
        ))
        rslt = objTask.run(**kwargs)
        self.logger.debug("Subtask {} returned {}".format(str(objTask), rslt))

    # Interfaces to run
    def invokeMain(self, ns):
        return self.main(ns)
    def runWithNs(self, ns):
        self.logger.debug("Invoked with parameters:\n{}".format(pformat(vars(ns))))
        self.logger.debug("Running Pre Hook...")
        self.invokeHook('preMain', ns)

        self.logger.debug("====== Begin Main Script ======")
        rslt = self.invokeMain(ns)
        self.logger.debug("====== End Main Script ======")

        self.logger.debug("Running Post Hook...")
        self.invokeHook('postMain', ns)
        return rslt
    def run(self, **kwargs):
        return self.runWithNs(SNS(**kwargs))
