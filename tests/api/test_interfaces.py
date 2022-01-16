import pytest

from pycaro.api.interfaces import SummarySingleMethod, SummarySingleModule
from pycaro.api.pycaro_types import UnstableModuleObject, UnstableVar


@pytest.fixture
def unstable_module_object():
    return UnstableModuleObject(
        module_object="fake-module",
        unstable_vars=[
            UnstableVar(
                var_name="var1", first_oc_line_no=5, line_preview="fake line for var1"
            )
        ],
    )


class A(SummarySingleMethod):
    def method_render(self, *args, **kwargs) -> str:
        return self.unstable_module_object.module_object

    def vars_render(self, *args, **kwargs) -> str:
        return "\n".join(
            (uv.var_name for uv in self.unstable_module_object.unstable_vars)
        )


class B(SummarySingleModule):
    def module_render(self, *args, **kwargs) -> str:
        return self.module_path


def test_summary_single_method(unstable_module_object,):

    rendered = A(unstable_module_object=unstable_module_object)

    assert rendered.method_render() == "fake-module"
    assert rendered.vars_render() == "var1"


def test_summary_single_module(unstable_module_object):
    rendered = B(
        module_path="path/to/module.py",
        methods_summaries=[
            A(unstable_module_object=unstable_module_object),
        ]
    )
    assert rendered.module_render() == "path/to/module.py"
