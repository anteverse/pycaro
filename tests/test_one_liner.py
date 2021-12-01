from pycaro import ModuleChecker


def test_one_liner():
    m = ModuleChecker(module_name="tests.assets.case_simple_one_liner")

    unstable_methods = list(m.unstable_methods)
    assert len(unstable_methods) == 1
    assert unstable_methods[0].method_name == "do_something"

    assert len(unstable_methods[0].unstable_vars) == 1
    assert unstable_methods[0].unstable_vars[0].var_name == "var"
    assert unstable_methods[0].unstable_vars[0].first_oc_line_no == 1
    assert unstable_methods[0].unstable_vars[0].line_preview == "def do_something(): print(var)"
