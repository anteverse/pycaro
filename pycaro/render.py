from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Iterable, List, Optional, Iterator

import click as click

from . import ModuleChecker
from .abstract import SummarySingleMethod, SummarySingleModule, SummaryStyleApplicator, TermColorStyleApplicator
from .pycaro_types import UnstableMethod, UnstableModule


class SimpleSummarySingleMethod(SummarySingleMethod):
    def method_render(self, *args, **kwargs) -> str:
        return f"  ↳ in method {self.unstable_method.method_name}"

    def vars_render(self, *args, **kwargs) -> List[str]:
        return [
            (
                f"    ↳ variable {unstable_var.var_name} at line {unstable_var.first_oc_line_no}: "
                f"{unstable_var.line_preview}"
            )
            for unstable_var in self.unstable_method.unstable_vars
        ]

@dataclass
class SimpleSummarySingleModule(SummarySingleModule):
    def module_render(self, *args, **kwargs) -> str:
        return f"* unstable var(s) found in {self.module_path}:"


stdout_summary_style_applicator = SummaryStyleApplicator(
    module_style_applicator=TermColorStyleApplicator(color="red"),
    method_style_applicator=TermColorStyleApplicator(color="cyan"),
    var_style_applicator=TermColorStyleApplicator(),
)


class StdoutSummary:
    def __init__(self,):
        self.style_applicator = stdout_summary_style_applicator

    @staticmethod
    def generate_module_summaries(entries: List[UnstableModule]) -> Iterator[SummarySingleModule]:
        for entry in entries:
            yield SimpleSummarySingleModule(
                module_path=entry.module_path,
                methods_summaries=[
                    SimpleSummarySingleMethod(
                        unstable_method=unstable_method
                    ) for unstable_method in entry.unstable_methods
                ]
            )

    def render(self, entries: List[UnstableModule] = None):
        if not entries:
            return

        yield from self.style_applicator.render(entries=self.generate_module_summaries(entries=entries))


@click.group("pycaro")
def _pycaro():
    pass


@_pycaro.command("test")
def _test():
    m = ModuleChecker(module_name="tests.assets.case_simple_one_liner")
    prepared_writer = StdoutSummary()

    for line in prepared_writer.render(entries=[m.as_unstable_module]):
        print(line)


if __name__ == '__main__':
    _test()