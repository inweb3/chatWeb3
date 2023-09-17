"""Callback Handler that logs debugging information"""
import logging
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import AgentAction, AgentFinish, LLMResult

from config.logging_config import get_logger

logger = get_logger(__name__)
# logger = get_logger(
#     __name__, log_level=logging.DEBUG, log_to_console=True, log_to_file=True
# )


class LoggerCallbackHandler(BaseCallbackHandler):
    """Callback Handler that prints to std out."""

    def __init__(self, color: Optional[str] = None) -> None:
        """Initialize callback handler."""
        self.color = color

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """Print out the prompts."""
        # class_name = serialized["name"]
        # class_name = serialized
        logger.debug(f"Starting lLM with prompts: {prompts}")

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Print out the response."""
        logger.debug(f"LLM response: {response}")

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """Print out new token."""
        logger.debug(f"LLM new token: {token}")

    def on_llm_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> None:
        """Print out LLM error."""
        logger.debug(f"LLM error: {error}")

    def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    ) -> None:
        """Print out that we are entering a chain."""
        # class_name = serialized["name"]
        # class_name = serialized
        logger.debug(f"\n\n\033[1m> Entering new chain\033[0m with inputs: {inputs}")
        # print(f"\n\n\033[1m> Entering new {class_name} chain...\033[0m")

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        """Print out that we finished a chain."""
        logger.debug(f"\n\033[1m> Finished chain.\033[0m with outputs: {outputs}")
        # print("\n\033[1m> Finished chain.\033[0m")

    def on_chain_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> None:
        """Print out chain error"""
        logger.debug(f"Chain error: {error}")

    def on_tool_start(
        self,
        serialized: Dict[str, Any],
        input_str: str,
        **kwargs: Any,
    ) -> None:
        """Print out tool start."""
        # tool_name = serialized["name"]
        # tool_description = serialized["description"]
        logger.debug(f"Starting tool: {serialized} with input: {input_str}")

    def on_agent_action(
        self, action: AgentAction, color: Optional[str] = None, **kwargs: Any
    ) -> Any:
        """Run on agent action."""
        # print_text(action.log, color=color if color else self.color)
        logger.debug(f"Agent action: {action}")

    def on_tool_end(
        self,
        output: str,
        color: Optional[str] = None,
        observation_prefix: Optional[str] = None,
        llm_prefix: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """If not the final action, print out observation."""
        if observation_prefix is not None:
            # print_text(f"\n{observation_prefix}")
            logger.debug(f"Not final action since {observation_prefix=} is not None")
        # print_text(output, color=color if color else self.color)
        logger.debug(f"Tool ended with {output=}")
        if llm_prefix is not None:
            # print_text(f"\n{llm_prefix}")
            logger.debug(f"{llm_prefix=} is not None, continue")

    def on_tool_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> None:
        """Print out tool error."""
        logger.debug(f"Tool error: {error}")

    def on_text(
        self,
        text: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Run when agent ends."""
        # print_text(text, color=color if color else self.color, end=end)
        logger.debug(f"on text: {text}")

    def on_agent_finish(
        self, finish: AgentFinish, color: Optional[str] = None, **kwargs: Any
    ) -> None:
        """Run on agent end."""
        logger.debug(f"Agent finished with {finish=}")

    def log_with_context(
        self, msg: str, pathname: str, lineno: int, func_name: str
    ) -> None:
        extra = {
            "pathname": pathname,
            "lineno": lineno,
            "funcName": func_name,
        }
        logger.debug(msg, extra=extra)
