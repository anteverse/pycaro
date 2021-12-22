import importlib
import re
from functools import lru_cache
from inspect import getsource
from pathlib import Path
from typing import Iterator, Optional, List

from .constants import BUILTIN_OBJECTS
from .files import find_project_root, get_path_from_root, get_absolute_path
from .logger import get_logger
from .pycaro_types import (
    UnstableVar,
    UnstableModuleObject,
    UnstableModule,
    FuncCoVarsAttr,
)

_logger = get_logger()


def _are_co_var_attributes(
    func,
) -> Iterator[FuncCoVarsAttr]:
    co_var_names = func.__code__.co_varnames
    source = getsource(func)
    for co_var_name in co_var_names:
        yield FuncCoVarsAttr(
            co_var_name=co_var_name, is_attribute=f".{co_var_name}" in source
        )


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
        file_path: Path,
    ):
        self.file_path = file_path
        self.root = find_project_root(())

        self.absolute_path = get_absolute_path(
            path=self.file_path,
            root=self.root,
        )
        self.file_path_normalized = get_path_from_root(
            path=self.absolute_path,
            root=self.root,
        )

        self.importable_module_path = self.file_path_normalized.replace(
            ".py", ""
        ).replace("/", ".")
        _logger.debug(self.importable_module_path)

        self.visited = importlib.import_module(
            self.importable_module_path,
        )

        visited_all_objects = vars(self.visited)
        self.valid_names = list(visited_all_objects.keys()) + list(
            visited_all_objects["__builtins__"].keys()
        )

        self.module_imported_objects = {
            obj_name
            for obj_name in visited_all_objects.keys()
            if not hasattr(visited_all_objects[obj_name], "__code__")
        }

        self.module_objects = {
            obj_name
            for obj_name in set(visited_all_objects.keys())
            .difference(set(BUILTIN_OBJECTS))
            .difference(self.module_imported_objects)
        }

    @property
    @lru_cache(None)
    def is_stable(self) -> bool:
        """
        Considered stable
        :return:
        """
        return (
            len(self.module_objects) == 0
            or len(list(map(self.get_method_var_names, self.module_objects))) == 0
        )

    def get_method_var_names(self, module_object: str) -> List[str]:
        """
        For a given method, return the names of local vars
        :param module_object: Name of the method to explore
        :return:
        """

        obj = vars(self.visited)[module_object]

        # locals
        used_var = vars(self.visited)[module_object].__code__.co_names

        # Remove builtins
        local_vars = set(used_var).difference(vars(self.visited)["__builtins__"].keys())

        # Remove imported
        local_vars = local_vars.difference(self.module_imported_objects)

        local_vars = local_vars.difference(
            {
                func_co_var_attr.co_var_name
                for func_co_var_attr in _are_co_var_attributes(obj)
                if func_co_var_attr.is_attribute
            }
        )

        return list(local_vars)

    def get_var_name_first_usage(
        self, module_object: str, var_name: str
    ) -> UnstableVar:
        # Patterns definition
        def_pattern = re.compile(rf"^\s*def\s{re.escape(module_object)}\(.*$")
        var_pattern = re.compile(rf"^.*[^\w]{re.escape(var_name)}[^\w|$]")

        with open(self.absolute_path.as_posix(), "r") as f:
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
            method_name=module_object,
            var_name=var_name,
        )

    def check(self, module_object: str):
        """
        Returns an index of all var names with their stability evaluation.
        :param module_object: The name of the method on which we check variables
        """
        return {
            var_name: var_name in self.valid_names
            for var_name in self.get_method_var_names(module_object=module_object)
        }

    def check_all(self):
        return [
            {"method_name": module_object, "check": self.check(module_object)}
            for module_object in self.module_objects
        ]

    @property
    def unstable_module_objects(self) -> Iterator[UnstableModuleObject]:
        """
        Generator property of all unstable module objects in the given module
        """
        for module_object in self.module_objects:

            # Check all vars of the given method {method_name}
            vars_checked = self.check(
                module_object=module_object,
            )
            if all(vars_checked.values()):
                # No need to go any further if all vars
                # are bounded for {method_name}
                continue

            # Build the list of unstable variables
            unstable_vars = [
                self.get_var_name_first_usage(
                    module_object=module_object,
                    var_name=var_name,
                )
                for var_name, stable in vars_checked.items()
                if not stable
            ]

            yield UnstableModuleObject(
                module_object=module_object,
                unstable_vars=unstable_vars,
            )

    @property
    @lru_cache(None)
    def as_unstable_module(self) -> Optional[UnstableModule]:
        if self.is_stable or next(self.unstable_module_objects) is None:
            return None
        return UnstableModule(
            module_path=self.file_path.as_posix(),
            unstable_module_objects=self.unstable_module_objects,
        )


class ModuleCollectionCheck:
    def __init__(self, paths: List[Path]):
        self.paths = paths

    def __iter__(self):
        pass

    def __next__(self):
        pass


def get_module_checker_generator(
    paths: List[Path],
) -> Optional[Iterator[ModuleChecker]]:
    """
    Generate a list of unstable module object after having checked that the module contains unstable methods
    :param paths: paths to scan
    :return:
    """
    for path in paths:
        checker = ModuleChecker(path)

        unstable = checker.as_unstable_module
        if unstable:
            yield unstable
