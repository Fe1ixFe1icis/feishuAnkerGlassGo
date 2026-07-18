"""LLM abstraction layer."""

from typing import TypeVar

from langchain_anthropic import ChatAnthropic
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from glassgo_workflow.config import (
    get_api_key,
    get_default_llm_provider,
    get_default_model,
    get_temperature,
    load_env,
)

load_env()

T = TypeVar("T")


def get_llm(
    provider: str | None = None,
    model: str | None = None,
    temperature: float | None = None,
) -> BaseChatModel:
    """Build a chat model instance based on provider and environment."""
    provider = provider or get_default_llm_provider()
    model = model or get_default_model(provider)
    temperature = temperature if temperature is not None else get_temperature()

    if provider == "openai":
        return ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=get_api_key("openai"),
        )
    if provider == "anthropic":
        return ChatAnthropic(
            model=model,
            temperature=temperature,
            api_key=get_api_key("anthropic"),
        )
    raise ValueError(f"Unsupported LLM provider: {provider}")


def build_messages(system_prompt: str, user_prompt: str) -> list[BaseMessage]:
    """Build a standard message pair."""
    return [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ]
