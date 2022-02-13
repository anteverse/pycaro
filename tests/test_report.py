import pytest

from pycaro.api.pycaro_types import UnstableModule, UnstableModuleObject, UnstableVar
from pycaro.report import StdoutSummary


def test_stdout_summary_empty():
    prepared_writer = StdoutSummary()
    res = list(prepared_writer.render(entries=None))

    assert res == []


@pytest.fixture
def unstable_module():
    return UnstableModule(
        module_path="path/to/module.py",
        unstable_module_objects=iter(
            [
                UnstableModuleObject(
                    module_object="func1",
                    unstable_vars=[
                        UnstableVar(
                            var_name="var1",
                            first_oc_line_no=5,
                            line_preview="fake line for var1",
                        )
                    ],
                )
            ]
        ),
    )


def test_stdout_summary_not_empty(unstable_module):
    prepared_writer = StdoutSummary()
    lines = list(prepared_writer.render(entries=iter([unstable_module])))

    assert len(lines) == 3

    assert lines == [
        "\x1b[31m* unstable var(s) found in path/to/module.py:\x1b[0m",
        "\x1b[36m  ↳ in method func1\x1b[0m",
        "    ↳ variable var1 at line 5: fake line for var1\x1b[0m",
    ]
