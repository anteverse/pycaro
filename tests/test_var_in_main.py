from pathlib import Path

from pycaro import ModuleChecker


def test_var_in_main():
    m = ModuleChecker(file_path=Path("tests/assets/case_simple_var_in_main.py"))
    res = m.check("do_something")
    assert res["var"] is False
    assert m.get_var_name_first_usage(module_object="do_something", var_name="var").first_oc_line_no == 5


def test_check_all():
    m = ModuleChecker(file_path=Path("tests/assets/case_simple_var_in_main.py"))

    unstable_module_objects = list(m.unstable_module_objects)
    assert len(unstable_module_objects) == 1
    assert unstable_module_objects[0].module_object == "do_something"

    assert len(unstable_module_objects[0].unstable_vars) == 1
    assert unstable_module_objects[0].unstable_vars[0].var_name == "var"
    assert unstable_module_objects[0].unstable_vars[0].first_oc_line_no == 5
    assert unstable_module_objects[0].unstable_vars[0].line_preview == "    print(var, var)"
