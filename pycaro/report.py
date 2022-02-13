from dataclasses import dataclass
from typing import Iterable, List, Iterator

from pycaro.api.interfaces import (
    SummarySingleMethod,
    SummarySingleModule,
    SummaryStyleApplicator,
    TermColorStyleApplicator,
)
from pycaro.api.pycaro_types import UnstableModule


class SimpleSummarySingleMethod(SummarySingleMethod):
    def method_render(self, *args, **kwargs) -> str:
        return f"  ↳ in method {self.unstable_module_object.module_object}"

    def vars_render(self, *args, **kwargs) -> List[str]:
        return [
            (
                f"    ↳ variable {unstable_var.var_name} at line {unstable_var.first_oc_line_no}: "
                f"{unstable_var.line_preview}"
            )
            for unstable_var in self.unstable_module_object.unstable_vars
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
    """
    Renderer using style applicators based on `termcolor`.

    Default for CLI.
    """
    def __init__(
        self,
    ):
        self.style_applicator = stdout_summary_style_applicator

    @staticmethod
    def generate_module_summaries(
        entries: Iterable[UnstableModule],
    ) -> Iterator[SummarySingleModule]:
        for entry in entries:
            yield SimpleSummarySingleModule(
                module_path=entry.module_path,
                methods_summaries=[
                    SimpleSummarySingleMethod(
                        unstable_module_object=unstable_module_object
                    )
                    for unstable_module_object in entry.unstable_module_objects
                ],
            )

    def render(self, entries: Iterable[UnstableModule] = None):
        if not entries:
            return

        yield from self.style_applicator.render(
            entries=self.generate_module_summaries(entries=entries)
        )
