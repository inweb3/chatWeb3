import time
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

from langchain.agents.agent import (
    AgentExecutor,
    BaseMultiActionAgent,
    BaseSingleActionAgent,
    ExceptionTool,
)
from langchain.agents.tools import InvalidTool
from langchain.callbacks.manager import (
    AsyncCallbackManagerForChainRun,
    CallbackManagerForChainRun,
    Callbacks,
)

# from langchain.llms import OpenAI
# from langchain.output_parsers import RetryWithErrorOutputParser
from langchain.schema import AgentAction, AgentFinish, OutputParserException
from langchain.tools.base import BaseTool
from langchain.utilities.asyncio import asyncio_timeout
from langchain.utils.input import get_color_mapping
from openai.error import InvalidRequestError

# from chatweb3.agents.chat.output_parser import ChatWeb3ChatOutputParser
# from chatweb3.agents.conversational_chat.output_parser import (
#    ChatWeb3ChatConvoOutputParser,
# )
# from config.config import agent_config
from config.logging_config import get_logger

logger = get_logger(__name__)
# logger = get_logger(
#     __name__, log_level=logging.DEBUG, log_to_console=True, log_to_file=True
# )

# CONVERSATION_MODE = agent_config.get("agent.conversational_chat")

# if CONVERSATION_MODE:
#     parser = ChatWeb3ChatConvoOutputParser()
# else:
#     parser = ChatWeb3ChatOutputParser()

# retry_parser = RetryWithErrorOutputParser.from_llm(
#     parser=parser, llm=OpenAI(temperature=0)
# )


class ChatWeb3AgentExecutor(AgentExecutor):
    @classmethod
    def from_agent_and_tools(
        cls,
        agent: Union[BaseSingleActionAgent, BaseMultiActionAgent],
        tools: Sequence[BaseTool],
        callbacks: Optional[Callbacks] = None,
        **kwargs: Any,
    ) -> "ChatWeb3AgentExecutor":
        """Create from agent and tools."""
        return cls(
            agent=agent,
            tools=tools,
            callbacks=callbacks,
            **kwargs,
        )

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
                    output_str = "Unfortunately, this question requires many thought steps that exceeded the context window length supported by the current AI model. Please try a different question, or a model that supports a larger context window needs to be used."
                else:
                    output_str = str(e)
                next_step_output = AgentFinish(
                    return_values={
                        "output": f'{output_str} \n\n Raw Error: "{str(e)}"'
                    },
                    log=f"Exception raised: {e}",
                )
                logger.error(
                    f"agent received {type(e).__name__} exception: {e}, \
                             created AgentFinish object"
                ),
            except OutputParserException as e:
                output_str = "Unfortunately, the AI model does not produce the expected next step actions to continue the thought process. Please try a different question, or a more capable AI model needs to be used."
                next_step_output = AgentFinish(
                    return_values={"output": str(e)},
                    log=f"{type(e).__name__} exception: {e}",
                )
                logger.error(
                    f"agent received {type(e).__name__} exception: {e}, \
                             created AgentFinish object"
                ),
            except Exception as e:
                next_step_output = AgentFinish(
                    return_values={"output": str(e)},
                    log=f"{type(e).__name__} exception: {e}",
                )
                logger.error(
                    f"agent received {type(e).__name__} exception: {e}, \
                             created AgentFinish object"
                ),

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

    # def _take_next_step(
    #     self,
    #     name_to_tool_map: Dict[str, BaseTool],
    #     color_mapping: Dict[str, str],
    #     inputs: Dict[str, str],
    #     intermediate_steps: List[Tuple[AgentAction, str]],
    #     run_manager: Optional[CallbackManagerForChainRun] = None,
    # ) -> Union[AgentFinish, List[Tuple[AgentAction, str]]]:
    #     """Take a single step in the thought-action-observation loop.

    #     Override this to take control of how the agent makes and acts on choices.
    #     """
    #     try:
    #         intermediate_steps = self._prepare_intermediate_steps(intermediate_steps)

    #         # Call the LLM to see what to do.
    #         output = self.agent.plan(
    #             intermediate_steps,
    #             callbacks=run_manager.get_child() if run_manager else None,
    #             **inputs,
    #         )
    #     except OutputParserException as e:
    #         if isinstance(self.handle_parsing_errors, bool):
    #             raise_error = not self.handle_parsing_errors
    #         else:
    #             raise_error = False
    #         if raise_error:
    #             raise e
    #         text = str(e)
    #         if isinstance(self.handle_parsing_errors, bool):
    #             if e.send_to_llm:
    #                 observation = str(e.observation)
    #                 text = str(e.llm_output)
    #             else:
    #                 observation = "Invalid or incomplete response"
    #         elif isinstance(self.handle_parsing_errors, str):
    #             observation = self.handle_parsing_errors
    #         elif callable(self.handle_parsing_errors):
    #             observation = self.handle_parsing_errors(e)
    #         else:
    #             raise ValueError("Got unexpected type of `handle_parsing_errors`")
    #         output = AgentAction("_Exception", observation, text)
    #         if run_manager:
    #             run_manager.on_agent_action(output, color="green")
    #         tool_run_kwargs = self.agent.tool_run_logging_kwargs()
    #         observation = ExceptionTool().run(
    #             output.tool_input,
    #             verbose=self.verbose,
    #             color=None,
    #             callbacks=run_manager.get_child() if run_manager else None,
    #             **tool_run_kwargs,
    #         )
    #         return [(output, observation)]
    #     # If the tool chosen is the finishing tool, then we end and return.
    #     if isinstance(output, AgentFinish):
    #         return output
    #     actions: List[AgentAction]
    #     if isinstance(output, AgentAction):
    #         actions = [output]
    #     else:
    #         actions = output
    #     result = []
    #     for agent_action in actions:
    #         if run_manager:
    #             run_manager.on_agent_action(agent_action, color="green")
    #         # Otherwise we lookup the tool
    #         if agent_action.tool in name_to_tool_map:
    #             tool = name_to_tool_map[agent_action.tool]
    #             return_direct = tool.return_direct
    #             color = color_mapping[agent_action.tool]
    #             tool_run_kwargs = self.agent.tool_run_logging_kwargs()
    #             if return_direct:
    #                 tool_run_kwargs["llm_prefix"] = ""
    #             # We then call the tool on the tool input to get an observation
    #             observation = tool.run(
    #                 agent_action.tool_input,
    #                 verbose=self.verbose,
    #                 color=color,
    #                 callbacks=run_manager.get_child() if run_manager else None,
    #                 **tool_run_kwargs,
    #             )
    #         else:
    #             tool_run_kwargs = self.agent.tool_run_logging_kwargs()
    #             observation = InvalidTool().run(
    #                 {
    #                     "requested_tool_name": agent_action.tool,
    #                     "available_tool_names": list(name_to_tool_map.keys()),
    #                 },
    #                 verbose=self.verbose,
    #                 color=None,
    #                 callbacks=run_manager.get_child() if run_manager else None,
    #                 **tool_run_kwargs,
    #             )
    #         result.append((agent_action, observation))
    #     return result

    # async def _atake_next_step(
    #     self,
    #     name_to_tool_map: Dict[str, BaseTool],
    #     color_mapping: Dict[str, str],
    #     inputs: Dict[str, str],
    #     intermediate_steps: List[Tuple[AgentAction, str]],
    #     run_manager: Optional[AsyncCallbackManagerForChainRun] = None,
    # ) -> Union[AgentFinish, List[Tuple[AgentAction, str]]]:
    #     """Take a single step in the thought-action-observation loop.

    #     Override this to take control of how the agent makes and acts on choices.
    #     """
    #     try:
    #         intermediate_steps = self._prepare_intermediate_steps(intermediate_steps)

    #         # Call the LLM to see what to do.
    #         output = await self.agent.aplan(
    #             intermediate_steps,
    #             callbacks=run_manager.get_child() if run_manager else None,
    #             **inputs,
    #         )
    #     except OutputParserException as e:
    #         if isinstance(self.handle_parsing_errors, bool):
    #             raise_error = not self.handle_parsing_errors
    #         else:
    #             raise_error = False
    #         if raise_error:
    #             raise e
    #         text = str(e)
    #         if isinstance(self.handle_parsing_errors, bool):
    #             if e.send_to_llm:
    #                 observation = str(e.observation)
    #                 text = str(e.llm_output)
    #             else:
    #                 observation = "Invalid or incomplete response"
    #         elif isinstance(self.handle_parsing_errors, str):
    #             observation = self.handle_parsing_errors
    #         elif callable(self.handle_parsing_errors):
    #             observation = self.handle_parsing_errors(e)
    #         else:
    #             raise ValueError("Got unexpected type of `handle_parsing_errors`")
    #         output = AgentAction("_Exception", observation, text)
    #         tool_run_kwargs = self.agent.tool_run_logging_kwargs()
    #         observation = await ExceptionTool().arun(
    #             output.tool_input,
    #             verbose=self.verbose,
    #             color=None,
    #             callbacks=run_manager.get_child() if run_manager else None,
    #             **tool_run_kwargs,
    #         )
    #         return [(output, observation)]
    #     # If the tool chosen is the finishing tool, then we end and return.
    #     if isinstance(output, AgentFinish):
    #         return output
    #     actions: List[AgentAction]
    #     if isinstance(output, AgentAction):
    #         actions = [output]
    #     else:
    #         actions = output

    #     async def _aperform_agent_action(
    #         agent_action: AgentAction,
    #     ) -> Tuple[AgentAction, str]:
    #         if run_manager:
    #             await run_manager.on_agent_action(
    #                 agent_action, verbose=self.verbose, color="green"
    #             )
    #         # Otherwise we lookup the tool
    #         if agent_action.tool in name_to_tool_map:
    #             tool = name_to_tool_map[agent_action.tool]
    #             return_direct = tool.return_direct
    #             color = color_mapping[agent_action.tool]
    #             tool_run_kwargs = self.agent.tool_run_logging_kwargs()
    #             if return_direct:
    #                 tool_run_kwargs["llm_prefix"] = ""
    #             # We then call the tool on the tool input to get an observation
    #             observation = await tool.arun(
    #                 agent_action.tool_input,
    #                 verbose=self.verbose,
    #                 color=color,
    #                 callbacks=run_manager.get_child() if run_manager else None,
    #                 **tool_run_kwargs,
    #             )
    #         else:
    #             tool_run_kwargs = self.agent.tool_run_logging_kwargs()
    #             observation = await InvalidTool().arun(
    #                 {
    #                     "requested_tool_name": agent_action.tool,
    #                     "available_tool_names": list(name_to_tool_map.keys()),
    #                 },
    #                 verbose=self.verbose,
    #                 color=None,
    #                 callbacks=run_manager.get_child() if run_manager else None,
    #                 **tool_run_kwargs,
    #             )
    #         return agent_action, observation

    #     # Use asyncio.gather to run multiple tool.arun() calls concurrently
    #     result = await asyncio.gather(
    #         *[_aperform_agent_action(agent_action) for agent_action in actions]
    #     )

    #     return list(result)
