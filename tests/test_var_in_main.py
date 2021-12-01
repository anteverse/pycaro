from pycaro import ModuleChecker


def test_var_in_main():
    m = ModuleChecker(module_name="tests.assets.case_simple_var_in_main")

    res = m.check("do_something")
    assert res["var"] is False
    assert res["print"] is True

    assert m.get_var_name_first_usage(method_name="do_something", var_name="var").first_oc_line_no == 5


def test_check_all():
    m = ModuleChecker(module_name="tests.assets.case_simple_var_in_main")

    unstable_methods = list(m.unstable_methods)
    assert len(unstable_methods) == 1
    assert unstable_methods[0].method_name == "do_something"

    assert len(unstable_methods[0].unstable_vars) == 1
    assert unstable_methods[0].unstable_vars[0].var_name == "var"
    assert unstable_methods[0].unstable_vars[0].first_oc_line_no == 5
    assert unstable_methods[0].unstable_vars[0].line_preview == "    print(var, var)"
