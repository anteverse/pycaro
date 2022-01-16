from dataclasses import dataclass
from typing import List, Iterator


@dataclass(frozen=True)
class FuncCoVarsAttr:
    co_var_name: str
    is_attribute: bool


@dataclass(frozen=True)
class UnstableVar:
    """
    For a variable considered unstable, get the first occurrence of it the analyzed method, and the matching line
    """

    var_name: str
    first_oc_line_no: int
    line_preview: str


@dataclass(frozen=True)
class UnstableModuleObject:
    """
    For a given method name, associate all Variable objects considered unstable
    """

    module_object: str
    unstable_vars: List[UnstableVar]


@dataclass
class UnstableModule:
    """
    For a given module path, associate all methods considered unstable
    """

    module_path: str
    unstable_module_objects: Iterator[UnstableModuleObject]

    def __post_init__(self):
        # TODO: remove check
        self.module_path = (
            self.module_path
            if self.module_path.endswith(".py")
            else self.module_path + ".py"
        )
