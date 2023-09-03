from typing import Any, Dict, List, Optional, Tuple
from langchain.agents.agent import AgentExecutor
from langchain.schema import AgentAction, AgentFinish
from langchain.callbacks.manager import (
    CallbackManagerForChainRun,
    AsyncCallbackManagerForChainRun,
)
from langchain.utils.input import get_color_mapping
from langchain.utilities.asyncio import asyncio_timeout
import time
from openai.error import InvalidRequestError


class chatWeb3AgentExecutor(AgentExecutor):
    def _call(
        self,
        inputs: Dict[str, str],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, Any]:
        """Run text through and get agent response."""
        # Construct a mapping of tool name to tool for easy lookup
        name_to_tool_map = {tool.name: tool for tool in self.tools}
        # We construct a mapping from each tool to a color, used for logging.
        color_mapping = get_color_mapping(
            [tool.name for tool in self.tools], excluded_colors=["green", "red"]
        )
        intermediate_steps: List[Tuple[AgentAction, str]] = []
        # Let's start tracking the number of iterations and time elapsed
        iterations = 0
        time_elapsed = 0.0
        start_time = time.time()
        # We now enter the agent loop (until it returns something).
        while self._should_continue(iterations, time_elapsed):
            try:
                next_step_output = self._take_next_step(
                    name_to_tool_map,
                    color_mapping,
                    inputs,
                    intermediate_steps,
                    run_manager=run_manager,
                )
            except InvalidRequestError as e:
                if "maximum context length" in str(e):
                    output_str = "Unfortunately, this question requires many thought steps that exceeded the context window length supported by the current AI model. Please try a different question or switch to a model that supports a larger context window."
                else:
                    output_str = str(e)
                next_step_output = AgentFinish(
                    return_values={
                        "output": f'{output_str} \n\n Raw Error: "{str(e)}"'
                    },
                    log=f"Exception raised: {e}",
                )
            except Exception as e:
                next_step_output = AgentFinish(
                    return_values={"output": str(e)},
                    log=f"Exception raised: {e}",
                )

            if isinstance(next_step_output, AgentFinish):
                return self._return(
                    next_step_output, intermediate_steps, run_manager=run_manager
                )

            intermediate_steps.extend(next_step_output)
            if len(next_step_output) == 1:
                next_step_action = next_step_output[0]
                # See if tool should return directly
                tool_return = self._get_tool_return(next_step_action)
                if tool_return is not None:
                    return self._return(
                        tool_return, intermediate_steps, run_manager=run_manager
                    )
            iterations += 1
            time_elapsed = time.time() - start_time

        output = self.agent.return_stopped_response(
            self.early_stopping_method, intermediate_steps, **inputs
        )
        return self._return(output, intermediate_steps, run_manager=run_manager)

    async def _acall(
        self,
        inputs: Dict[str, str],
        run_manager: Optional[AsyncCallbackManagerForChainRun] = None,
    ) -> Dict[str, str]:
        """Run text through and get agent response."""
        # Construct a mapping of tool name to tool for easy lookup
        name_to_tool_map = {tool.name: tool for tool in self.tools}
        # We construct a mapping from each tool to a color, used for logging.
        color_mapping = get_color_mapping(
            [tool.name for tool in self.tools], excluded_colors=["green"]
        )
        intermediate_steps: List[Tuple[AgentAction, str]] = []
        # Let's start tracking the number of iterations and time elapsed
        iterations = 0
        time_elapsed = 0.0
        start_time = time.time()
        # We now enter the agent loop (until it returns something).
        async with asyncio_timeout(self.max_execution_time):
            try:
                while self._should_continue(iterations, time_elapsed):
                    try:
                        next_step_output = await self._atake_next_step(
                            name_to_tool_map,
                            color_mapping,
                            inputs,
                            intermediate_steps,
                            run_manager=run_manager,
                        )
                    except InvalidRequestError as e:
                        if "maximum context length" in str(e):
                            output_str = "Unfortunately, this question requires many thought steps that exceeded the context window length supported by the current AI model. Please try a different question or switch to a model that supports a larger context window."
                        else:
                            output_str = str(e)
                        next_step_output = AgentFinish(
                            return_values={
                                "output": f"{output_str} \n\n Raw error: '{str(e)}'"
                            },
                            log=f"Exception raised: {e}",
                        )
                    except Exception as e:
                        next_step_output = AgentFinish(
                            return_values={"output": str(e)},
                            log=f"Exception raised: {e}",
                        )

                    if isinstance(next_step_output, AgentFinish):
                        return await self._areturn(
                            next_step_output,
                            intermediate_steps,
                            run_manager=run_manager,
                        )

                    intermediate_steps.extend(next_step_output)
                    if len(next_step_output) == 1:
                        next_step_action = next_step_output[0]
                        # See if tool should return directly
                        tool_return = self._get_tool_return(next_step_action)
                        if tool_return is not None:
                            return await self._areturn(
                                tool_return, intermediate_steps, run_manager=run_manager
                            )

                    iterations += 1
                    time_elapsed = time.time() - start_time
                output = self.agent.return_stopped_response(
                    self.early_stopping_method, intermediate_steps, **inputs
                )
                return await self._areturn(
                    output, intermediate_steps, run_manager=run_manager
                )
            except TimeoutError:
                # stop early when interrupted by the async timeout
                output = self.agent.return_stopped_response(
                    self.early_stopping_method, intermediate_steps, **inputs
                )
                return await self._areturn(
                    output, intermediate_steps, run_manager=run_manager
                )
