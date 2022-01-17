from pathlib import Path

from pycaro import ModuleChecker


def test_one_liner():
    m = ModuleChecker(file_path=Path("tests/use_cases/assets/case_simple_one_liner.py"))

    unstable_module_objects = list(m.unstable_module_objects)
    assert len(unstable_module_objects) == 1
    assert unstable_module_objects[0].module_object == "do_something"

    assert len(unstable_module_objects[0].unstable_vars) == 1
    assert unstable_module_objects[0].unstable_vars[0].var_name == "var"
    assert unstable_module_objects[0].unstable_vars[0].first_oc_line_no == 1
    assert (
        unstable_module_objects[0].unstable_vars[0].line_preview
        == "def do_something(): print(var)"
    )
