"""
Utility functions for LLM completions using Pydantic AI.
"""

from typing import Any, Callable, get_type_hints

import pydantic_ai
from pydantic_ai import RunContext
from pydantic_ai.messages import (
    ModelRequest,
    ModelResponse,
    SystemPromptPart,
    TextPart,
    UserPromptPart,
)
from pydantic_ai.models import KnownModelName, Model, ModelSettings
from pydantic_ai.result import RunResult
from typing_extensions import TypeVar

import marvin

# Define Message type union
Message = ModelRequest | ModelResponse


def SystemMessage(content: str) -> ModelRequest:
    return ModelRequest(parts=[SystemPromptPart(content=content)])


def UserMessage(content: str) -> ModelRequest:
    return ModelRequest(parts=[UserPromptPart(content=content)])


def AgentMessage(content: str) -> ModelResponse:
    return ModelResponse(parts=[TextPart(content=content)])


# Type variable for generic response types
T = TypeVar("T")


def bind_tool(agent: pydantic_ai.Agent[Any, Any], func: Callable[..., Any]) -> None:
    """Bind a function as a tool to an agent.

    Inspects the function signature to see if it accepts a RunContext parameter.
    If it does, uses agent.tool(), otherwise uses agent.tool_plain().

    Args:
        agent: The Pydantic AI agent to bind the tool to
        func: The function to bind as a tool
    """
    # Get type hints including RunContext if present
    type_hints = get_type_hints(func)

    # Check if any parameter is annotated as RunContext
    has_run_context = any(hint == RunContext for hint in type_hints.values())

    # Use the appropriate method
    if has_run_context:
        agent.tool()(func)
    else:
        agent.tool_plain()(func)


def create_agentlet(
    model: KnownModelName | Model,
    result_type: type[T],
    tools: list[Callable[..., Any]] | None = None,
    deps_type: type[T] | None = None,
    model_settings: ModelSettings | None = None,
) -> pydantic_ai.Agent[Any, Any]:
    kwargs: dict[str, Any] = {}
    if tools:
        kwargs["tools"] = list(set(tools))
    if model_settings:
        kwargs["model_settings"] = model_settings

    agentlet = pydantic_ai.Agent[deps_type, result_type](
        model=model,
        result_type=result_type,
        retries=marvin.settings.agent_retries,
        **kwargs,
    )

    return agentlet


async def generate_response(
    agentlet: pydantic_ai.Agent[Any, Any],
    messages: list[Message] | None = None,
    user_prompt: str | None = None,
) -> RunResult:
    user_prompt = user_prompt or ""
    return await agentlet.run(user_prompt=user_prompt, message_history=messages)
