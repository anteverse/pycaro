from dataclasses import dataclass, field
from typing import List, Iterable, Iterator


@dataclass(frozen=True)
class UnstableVar:
    """
    For a variable considered unstable, get the first occurrence of it the analyzed method, and the matching line
    """

    var_name: str
    first_oc_line_no: int
    line_preview: str


@dataclass(frozen=True)
class UnstableMethod:
    """
    For a given method name, associate all Variable objects considered unstable
    """

    method_name: str
    unstable_vars: List[UnstableVar]


@dataclass
class UnstableModule:
    """
    For a given module path, associate all methods considered unstable
    """

    module_path: str
    unstable_methods: Iterator[UnstableMethod]

    def __post_init__(self):
        self.module_path = (
            self.module_path
            if self.module_path.endswith(".py")
            else self.module_path + ".py"
        )
