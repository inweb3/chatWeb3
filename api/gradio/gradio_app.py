"""
path: api/gradio/gradio_app.py
This file contains the main code for the chatbot application.
"""

import datetime
import os
import re

# from dotenv import load_dotenv
import gradio as gr  # type: ignore
from dotenv import load_dotenv

from chatweb3.create_agent import create_agent_executor
from config.config import agent_config
from config.logging_config import get_logger
from langchain.schema import AgentAction

logger = get_logger(__name__)
# logger = get_logger(
#     __name__, log_level=logging.DEBUG, log_to_console=True, log_to_file=True
# )


load_dotenv()

CONVERSATION_MODE = agent_config.get("agent.conversational_chat")


def set_openai_api_key(api_key, agent):
    """
    Set the OpenAI API Key to the provided value and create an agent executor.

    Parameters:
    api_key (str): OpenAI API Key
    agent: The agent to execute tasks

    Returns:
    agent_executor: The created agent executor
    """
    if api_key:
        # set the OpenAI API Key
        os.environ["OPENAI_API_KEY"] = api_key
        agent_executor = create_agent_executor(conversation_mode=CONVERSATION_MODE)
        os.environ["OPENAI_API_KEY"] = ""
        return agent_executor


def clean_text(text):
    text = re.sub(r"`|\\", "", str(text))  # remove problematic characters
    return text.strip().replace("\n", "\n  ")


def format_agent_action(agent_action_data, step_number):
    # print(f"{agent_action_data=}, {step_number=}")
    tool = agent_action_data.tool
    tool_input = agent_action_data.tool_input
    log_text = clean_text(agent_action_data.log)

    if not log_text.startswith("Thought:"):
        log_text = "Thought: " + log_text

    # Now, since we ensured 'Thought:' is present,
    # we can extract the text between 'Thought:' and 'Action:'
    thought_text = log_text.split("Thought:")[1].split("Action:")[0].strip()

    agent_action_text = (
        f"**Thought {step_number}**: {thought_text}"
        f"\n\n*Action:*\n\nTool: {tool}"
        f"\n\nTool input: {tool_input}"
    )

    # print(f"{agent_action_text=}")
    return agent_action_text


def format_observation(observation):
    # print(f"{observation=}")
    if isinstance(observation, list):
        # print(f"observation is a list")
        formatted_observation = "\n".join(
            [f"*Observation*: {clean_text(item)}" for item in observation]
        )
        # print(f"{formatted_observation=}")
    else:
        # print(f"observation is not a list")
        formatted_observation = f"*Observation*: {clean_text(observation)}"
        # print(f"{formatted_observation=}")

    observation_text = formatted_observation
    # observation_text = formatted_observation.replace("*Observation*: ", "")
    return observation_text


def format_response(response: dict) -> str:
    formatted_steps = []
    for i, step in enumerate(response["intermediate_steps"], start=1):
        # print(f"{i=}, {step=}")
        if isinstance(step[0], AgentAction):
            # print(f"step[0] is an AgentAction")
            formatted_steps.append(format_agent_action(step[0], i))
            # print(f"{formatted_steps=}")
            for item in step[1:]:
                formatted_steps.append(format_observation(item))
                # print(f"{formatted_steps=}")
        else:
            formatted_steps.append(format_observation(step[0]))
            # print(f"{formatted_steps=}")

    formatted_output = "\n\n".join(formatted_steps)
    # print(f"{formatted_output=}")

    if CONVERSATION_MODE:
        # print(f"CONVERSATION_MODE is True")
        chat_messages = "\n\n".join(
            [
                f"**{msg.__class__.__name__}**: {msg.content}"
                for msg in response.get("chat_history", [])
            ]
        )
        formatted_output = f"{chat_messages}\n\n{formatted_output}"
        # print(f"{formatted_output=}")
    else:
        # print(f"CONVERSATION_MODE is False")
        formatted_output += f"\n\n**Final answer**: {response['output']}"
        # print(f"{formatted_output=}")

    return formatted_output


def chat(inp, history, agent):
    """
    Handles the chat conversation. If the agent is None,
    it adds a message to the history asking for the OpenAI API Key.
    If the agent is set, it generates a response to the user's input and
    adds it to the history.

    Parameters:
    inp (str): The user's input
    history (list): The chat history
    agent: The chat agent

    Returns:
    history: The updated chat history
    thought_process_text: The formatted thought process text
    """

    # add code to check whether the FLIPSIDE_API_KEY is set,
    # if not, then raise an error message
    if not os.environ.get("FLIPSIDE_API_KEY"):
        raise Exception(
            "FLIPSIDE_API_KEY is not set, \
                        please set it in .env file or in the environment variable"
        )

    history = history or []
    if agent is None:
        history.append((inp, "Please paste your OpenAI API Key to use"))
        thought_process_text = "Please paste your OpenAI API Key to use"
        return history, history, thought_process_text
    else:
        print("\n==== date/time: " + str(datetime.datetime.now()) + " ====")
        print("inp: " + inp)
        try:
            response = agent(inp)
            try:
                answer = str(response["output"])
                logger.debug(f"answer: {answer}")
                thought_process_text = format_response(response)
                history.append((inp, answer))
            except Exception as e:
                logger.error(
                    f"{type(e).__name__=} exception from parsing {response=}: {e}"
                ),
                thought_process_text = f"Exception in parsing response: {e}"
                history.append((inp, thought_process_text))
        except Exception as e:
            logger.error(f"{type(e).__name__} exception from receiving response: {e}"),
            thought_process_text = f"Exception in receiving response: {e}"
            history.append((inp, thought_process_text))

    return history, history, thought_process_text

    # return history, history, "\n".join(thought_process_text)


block = gr.Blocks(css=".gradio-container {background-color: #f5f5f5;}")

with block:
    # first row contains the title and the api key textbox
    with gr.Row():
        gr.Markdown("<h3><center>Let's ChatWeb3 !</center></h3>")

        openai_api_key_textbox = gr.Textbox(
            placeholder="Paste your OpenAI API Key here",
            show_label=False,
            lines=1,
            type="password",
        )

    # second row contains the chatbot
    chatbot = gr.Chatbot()

    # third row contains the question textbox and the submit button
    with gr.Row():
        message = gr.Textbox(
            label="What's your question?",
            placeholder="What is the total daily trading volume on Uniswap in USD "
            "in the last 7 days?",
            lines=1,
        )
        submit = gr.Button(value="Send", variant="Secondary")
        # submit = gr.Button(value="Send", variant="Secondary").style(full_width=False)

    gr.Examples(
        examples=[
            "What is yesterday's total trading volume on Uniswap in USD?",
            "What is the total daily trading volume on Uniswap in USD "
            "in the last 7 days?",
        ],
        inputs=message,
    )

    # gr.HTML(
    #     "<center> Built by <a href='https://inweb3.com/'>inWeb3</a>"
    # )

    gr.HTML(
        "<center> Built by <a href='https://inweb3.com/'>inWeb3</a>, "
        "Powered by <a href='https://openai.com/'>OpenAI</a>, "
        "<a href='https://github.com/hwchase17/langchain'>LangChain 🦜️🔗</a>, "
        "<a href='https://flipsidecrypto.xyz/'>Flipsidecrypto</a></center>"
    )

    state = gr.State()  # this holds the chat history
    agent_state = gr.State()  # this is the agent

    with gr.Row():
        with gr.Column():
            thought_process_label = gr.Markdown("<h4>Thought process:</h4>")
            thought_process_text = gr.Markdown(value="")

    # "submit" Button.click is triggered when the user clicks the button
    submit.click(
        chat,
        inputs=[message, state, agent_state],
        # outputs=[chatbot, state, thought_process_textbox],
        outputs=[chatbot, state, thought_process_text],
    )

    message.submit(
        chat,
        inputs=[message, state, agent_state],
        outputs=[chatbot, state, thought_process_text],
    )

    # configure the "openai_api_key_textbox" textbox to change
    openai_api_key_textbox.change(
        set_openai_api_key,
        inputs=[openai_api_key_textbox, agent_state],
        outputs=[agent_state],
    )


def start(debug=False):
    try:
        logger.info("Starting Gradio app...")
        block.launch(debug=debug)
        logger.info("Gradio app started successfully!")
    except Exception as e:
        logger.error(f"Error while starting Gradio app: {e}")


# def start(debug=True):
#     block.launch(debug=debug)

# def format_response(response: dict) -> str:
#     logger.debug(f"response: {response}")

#     formatted_steps = []
#     for i, step in enumerate(response["intermediate_steps"], start=1):
#         agent_action_data, text = step
#         tool = agent_action_data.tool
#         tool_input = agent_action_data.tool_input
#         log = agent_action_data.log

#         text = clean_text(text)
#         if CONVERSATION_MODE:
#             formatted_steps.append(f"*Action*: {tool}\n\n*Observation*: {text}")
#         else:
#             thought, action = log.strip().split("\nAction:")
#             thought = thought.replace("Thought: ", "") if i == 1 else thought
#             formatted_steps.append(
#                 f"**Thought {i}**: {thought}\n\n*Action:*\n\nTool: {tool}"
#                 f"\n\nTool input: {tool_input}\n\n*Observation:*\n\n{text}"
#             )

# def format_response(response: dict) -> str:
#     logger.debug(f"response: {response}")

#     formatted_steps = []
#     for i, step in enumerate(response["intermediate_steps"], start=1):
#         # Unpack step based on its length
#         if len(step) == 2:
#             agent_action_data, text = step
#         else:
#             agent_action_data = None
#             text = step[0]

#         text = clean_text(text)

#         if CONVERSATION_MODE:
#             formatted_steps.append(f"*Action*: {agent_action_data.tool if agent_action_data else 'Unknown'}\n\n*Observation*: {text}")
#         else:
#             if agent_action_data and 'Thought:' in agent_action_data.log:
#                 thought = agent_action_data.log.split("\nAction:")[0].replace("Thought: ", "").strip()
#                 formatted_steps.append(
#                     f"**Thought {i}**: {thought}\n\n*Action:*\n\nTool: {agent_action_data.tool}"
#                     f"\n\nTool input: {agent_action_data.tool_input}\n\n*Observation:*\n\n{text}"
#                 )
#             else:
#                 formatted_steps.append(f"*Observation*: {text}")

#     formatted_output = "\n\n".join(formatted_steps)

#     if CONVERSATION_MODE:
#         chat_messages = "\n\n".join(
#             [
#                 f"**{msg.__class__.__name__}**: {msg.content}"
#                 for msg in response.get("chat_history", [])
#             ]
#         )
#         formatted_output = f"{chat_messages}\n\n{formatted_output}"
#     else:
#         formatted_output += f"\n\n**Final answer**: {response['output']}"

#     return formatted_output

# def format_response(response: dict) -> str:
#     logger.debug(f"response: {response}")

#     formatted_steps = []
#     for i, step in enumerate(response["intermediate_steps"], start=1):
#         # Check if the step contains an AgentAction
#         if isinstance(step[0], AgentAction):
#             agent_action_data = step[0]
#             tool = agent_action_data.tool
#             tool_input = agent_action_data.tool_input
#             log_text = clean_text(agent_action_data.log)
#             # print(f"{log_text=}")

#             if 'Thought:' not in log_text:
#                 log_text = "Thought: " + log_text

#             # Now, since we ensured 'Thought:' is present,
#             # we can extract the text between 'Thought:' and 'Action:'
#             thought_text = log_text.split('Thought:')[1].split('Action:')[0].strip()

#             formatted_steps.append(
#                 f"**Thought {i}**: {thought_text}"
#                 f"\n\n*Action:*\n\nTool: {tool}"
#                 f"\n\nTool input: {tool_input}"
#             )

#             # Format the remaining items in the step
#             for item in step[1:]:
#                 if isinstance(item, str):
#                     formatted_steps.append(f"*Observation*: {clean_text(item)}")
#                 elif isinstance(item, list):
#                     for list_item in item:
#                         formatted_steps.append(
#                             f"*Observation*: {clean_text(list_item)}"
#                             )
#                 # Additional types can be added here as needed

#         else:
#             # This step contains only a string or other type
#             formatted_steps.append(f"*Observation*: {clean_text(step[0])}")

#     formatted_output = "\n\n".join(formatted_steps)

#     if CONVERSATION_MODE:
#         chat_messages = "\n\n".join(
#             [
#                 f"**{msg.__class__.__name__}**: {msg.content}"
#                 for msg in response.get("chat_history", [])
#             ]
#         )
#         formatted_output = f"{chat_messages}\n\n{formatted_output}"
#     else:
#         formatted_output += f"\n\n**Final answer**: {response['output']}"

#     return formatted_output
