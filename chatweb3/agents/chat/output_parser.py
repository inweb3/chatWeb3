from langchain.agents.chat.output_parser import ChatOutputParser, FINAL_ANSWER_ACTION
import json
import re
from typing import Union
from json.decoder import JSONDecodeError

from langchain.schema import AgentAction, AgentFinish, OutputParserException

from chatweb3.agents.chat.prompt import SNOWFLAKE_FORMAT_INSTRUCTIONS


class ChatWeb3ChatOutputParser(ChatOutputParser):
    def get_format_instructions(self) -> str:
        return SNOWFLAKE_FORMAT_INSTRUCTIONS

    def parse(self, text: str) -> Union[AgentAction, AgentFinish]:
        includes_answer = FINAL_ANSWER_ACTION in text

        # 1. Try the default behavior
        try:
            found = self.pattern.search(text)
            if not found:
                raise ValueError("action not found")
            action = found.group(1)
            response = json.loads(action.strip())
            includes_action = "action" in response
            if includes_answer and includes_action:
                raise OutputParserException(
                    "Parsing LLM output produced a final answer "
                    f"and a parse-able action: {text}"
                )
            return AgentAction(
                response["action"], response.get("action_input", {}), text
            )
        except JSONDecodeError:
            # 2. Check for multiple enclosures
            all_matches = re.findall(r"`{3}(?:json)?\n(.*?)`{3}", text, re.DOTALL)
            if len(all_matches) > 1:
                # 3. Specific capture after "Action:"
                action_pattern = re.compile(
                    r"Action:.*?`{3}(?:json)?\n(.*?)`{3}", re.DOTALL
                )  # noqa E501
                found = action_pattern.search(text)
                if found:
                    try:
                        action = found.group(1)
                        response = json.loads(action.strip())
                        return AgentAction(
                            response["action"], response.get("action_input", {}), text
                        )
                    except JSONDecodeError:
                        # If still can't parse, raise an error
                        raise OutputParserException(
                            f"Could not parse LLM output after Action: {text}"
                        )

        except Exception:
            if not includes_answer:
                raise OutputParserException(f"Could not parse LLM output: {text}")
            output = text.split(FINAL_ANSWER_ACTION)[-1].strip()
            return AgentFinish({"output": output}, text)
