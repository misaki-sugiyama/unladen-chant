import pytest
from unladenchant.overrideenforcer import MetaMixinOverrideEnforcer

class MetaClassTest(MetaMixinOverrideEnforcer, type):
    pass

class BaseClass(metaclass=MetaClassTest):
    ISABSTRACTCLASS = True
    @mustBeOverriden
    def main(self):
        pass

def test_will_pass_if_overriden():
    class NewClass(BaseClass):
        def main(self):
            pass

def test_will_fail_if_not_overriden():
    with pytest.raises(NotImplementedError):
        class NewClass(BaseClass):
            pass

def test_cannot_instantiate_abstract_class():
    with pytest.raises(TypeError):
        obj = BaseClass()

def test_can_accept_init_args():
    class NewClass(BaseClass):
        def main(self):
            pass
    obj = NewClass(1,2,3)
