from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import List, Iterator, Iterable

from termcolor import colored

from pycaro.api.pycaro_types import UnstableModuleObject


@dataclass
class SummarySingleMethod(metaclass=ABCMeta):
    unstable_module_object: UnstableModuleObject

    @abstractmethod
    def method_render(self, *args, **kwargs) -> str:
        raise NotImplementedError

    @abstractmethod
    def vars_render(self, *args, **kwargs) -> str:
        raise NotImplementedError


@dataclass
class SummarySingleModule:
    module_path: str
    methods_summaries: List[SummarySingleMethod]

    @abstractmethod
    def module_render(self, *args, **kwargs) -> str:
        raise NotImplementedError


@dataclass
class StyleApplicator(metaclass=ABCMeta):
    def apply(
        self,
        text: str
    ):
        return text


@dataclass
class TermColorStyleApplicator(StyleApplicator):
    color: str = None
    highlight: str = None
    attributes: List[str] = None

    def apply(self, text: str):
        return colored(
            text=text, color=self.color, on_color=self.highlight, attrs=self.attributes
        )


@dataclass
class SummaryStyleApplicator:
    module_style_applicator: StyleApplicator
    method_style_applicator: StyleApplicator
    var_style_applicator: StyleApplicator

    def render(self, entries: Iterable[SummarySingleModule], *args, **kwargs) -> Iterator[str]:
        for entry in entries:
            yield self.module_style_applicator.apply(
                text=entry.module_render(*args, **kwargs),
            )
            for method_summary in entry.methods_summaries:
                yield self.method_style_applicator.apply(
                    text=method_summary.method_render(*args, **kwargs)
                )
                yield from (
                    self.var_style_applicator.apply(text=rendered_var)
                    for rendered_var in method_summary.vars_render(*args, **kwargs)
                )
