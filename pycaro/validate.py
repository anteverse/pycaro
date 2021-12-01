import importlib
import re
from typing import Iterator

from .constants import BUILTIN_OBJECTS
from .files import find_project_root
from .pycaro_types import UnstableVar, UnstableMethod, UnstableModule


class VarNotFoundInMethodException(Exception):
    """ """

    def __init__(self, method_name: str, var_name: str, *args):
        self.method_name = method_name
        self.var_name = var_name
        super(
            f"Could not find the var `{self.var_name}` in `{self.method_name}`", *args
        )


class ModuleChecker:
    def __init__(
        self,
        module_name: str,
    ):
        self.module_name = module_name

        self.file_path = find_project_root(()).joinpath(
            self.module_name.replace(".", "/")
        )

        self.visited = importlib.import_module(
            self.module_name,
        )

        visited_all_objects = vars(self.visited)
        self.valid_names = list(visited_all_objects.keys()) + list(
            visited_all_objects["__builtins__"].keys()
        )
        self.methods = set(visited_all_objects.keys()).difference(set(BUILTIN_OBJECTS))

    def get_method_var_names(self, method_name: str):
        """
        For a given method, return the names of local vars
        :param method_name: Name of the method to explore
        :return:
        """
        return vars(self.visited)[method_name].__code__.co_names

    def get_var_name_first_usage(self, method_name: str, var_name: str) -> UnstableVar:
        # Patterns definition
        def_pattern = re.compile(rf"^\s*def\s{re.escape(method_name)}\(.*$")
        var_pattern = re.compile(rf"^.*[^\w]{re.escape(var_name)}[^\w|$]")

        with open(self.file_path.as_posix() + ".py", "r") as f:
            lines = f.readlines()

            # Find the definition starting line
            for i, line in enumerate(lines):
                if def_pattern.match(line):
                    break

            # Once the definition starting line is found, find the
            # var name first occurrence and return
            for j, method_line in enumerate(lines[i:]):
                if var_pattern.match(method_line):
                    return UnstableVar(
                        var_name=var_name,
                        first_oc_line_no=i + 1 + j,
                        line_preview=method_line.rstrip("\n"),
                    )

        # We should not end up here. Right now this helps find uncharted patterns
        raise VarNotFoundInMethodException(
            method_name=method_name,
            var_name=var_name,
        )

    def check(self, method_name: str):
        """
        Returns an index of all var names with their stability evaluation.
        :param method_name: The name of the method on which we check variables
        """
        return {
            var_name: var_name in self.valid_names
            for var_name in self.get_method_var_names(method_name=method_name)
        }

    def check_all(self):
        return [
            {"method_name": method_name, "check": self.check(method_name)}
            for method_name in self.methods
        ]

    @property
    def unstable_methods(self) -> Iterator[UnstableMethod]:
        """
        Generator property of all unstable methods in the given module
        """
        for method_name in self.methods:

            # Check all vars of the given method {method_name}
            vars_checked = self.check(
                method_name=method_name,
            )
            if all(vars_checked.values()):
                # No need to go any further if all vars
                # are bounded for {method_name}
                continue

            # Build the list of unstable variables
            unstable_vars = [
                self.get_var_name_first_usage(
                    method_name=method_name,
                    var_name=var_name,
                )
                for var_name, stable in vars_checked.items()
                if not stable
            ]

            yield UnstableMethod(
                method_name=method_name,
                unstable_vars=unstable_vars,
            )

    @property
    def as_unstable_module(self) -> UnstableModule:
        return UnstableModule(
            # TODO: change name to path
            module_path=self.module_name,
            unstable_methods=self.unstable_methods,
        )
