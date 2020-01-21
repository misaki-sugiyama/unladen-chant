from .unladentaskbase import MetaClassUnladenTask

from argparse import ArgumentParser
from pkg_resources import get_distribution
from types import SimpleNamespace as SNS
from inspect import ismethod
import sys

class MixinCommandLine(metaclass=MetaClassUnladenTask):
    ISABSTRACTCLASS = True
    @classmethod
    def args(cls, parser): # pragma: no cover
        pass

    @hook('onClassCreation')
    def hook_create_args(cls):
        parser = ArgumentParser(allow_abbrev=False, description=cls.__doc__)
        cls.invokeHook('args', parser)
        # Force args to be classmethod no matter what
        if not ismethod(cls.args):
            cls.args = classmethod(cls.args)
        cls.args(parser)
        cls.parser = parser
        cls._defaults = vars(parser.parse_args(()))

    def __init__(self, *args, **kwargs):
        if kwargs:
            self._defaults = {**self._defaults, **kwargs}
        return super().__init__(*args)

    def runcmd(self, args=()):
        # Deliberately not putting this into args, so there won't be default value in args
        if len(args) > 0 and args[0] == '--version':
            print(get_distribution('unladen-chant').version)
            sys.exit(0)

        self.invokeHook('preParse', args)
        ns = self.parser.parse_args(args, namespace=SNS(**self._defaults))
        self.run(**vars(ns))

    def run(self, **kwargs):
        # Merge kwargs with defaults
        kwargsNew = {**self._defaults, **kwargs}
        return super().run(**kwargsNew)
