"""Base agent enforcing memory isolation."""

from abc import ABC
from typing import Any, TypeVar

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage

from glassgo_workflow.llm import build_messages

T = TypeVar("T")


class BaseAgent(ABC):
    """Abstract base for all workflow agents.

    Subclasses expose their own stage-specific methods (e.g. gather_parallel,
    diverge, attack). Memory isolation is enforced by only passing declared
    upstream outputs into each method's prompt.
    """

    def __init__(self, llm: BaseChatModel):
        self.llm = llm

    def _build_messages(self, system_prompt: str, user_prompt: str) -> list[BaseMessage]:
        return build_messages(system_prompt, user_prompt)

    def _invoke_structured(self, messages: list[BaseMessage], output_schema: type[T]) -> T:
        structured = self.llm.with_structured_output(output_schema)
        return structured.invoke(messages)
