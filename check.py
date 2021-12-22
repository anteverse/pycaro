from typing import Tuple

from pycaro import ModuleChecker
from pycaro.files import get_files
from pycaro.render import StdoutSummary


def check(src: Tuple[str, ...]):
    prepared_writer = StdoutSummary()

    for line in prepared_writer.render(
        entries=(
            ModuleChecker(path).as_unstable_module
            for path in get_files(src)
            if ModuleChecker(path).as_unstable_module
        )
    ):
        print(line)


if __name__ == "__main__":
    check(src=("tests/assets/",))
