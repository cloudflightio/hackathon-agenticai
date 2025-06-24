import mlflow
import chainlit as cl
import asyncio
from agent_hackathon.agent_models import (
    main_agent,
    account_billing_agent,
    order_management_agent,
    product_support_agent,
)
from openai import AsyncAzureOpenAI, OpenAIError, AuthenticationError
from agents import (
    Agent,
    Runner,
    OpenAIChatCompletionsModel,
    ModelSettings,
    set_tracing_disabled,
    TResponseInputItem,
)
from loguru import logger
import requests

# Check if MLFlow is running
tracking_uri = "http://localhost:5000"
try:
    health_check_url = f"{tracking_uri}/api/2.0/mlflow/experiments/list"
    requests.get(health_check_url)

    # If sucessful, setup MLFlow
    # Enable auto tracing for OpenAI Agents SDK
    mlflow.openai.autolog(silent=True)
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment("Agentic Hackathon")
except Exception as e:
    print(f"MLFlow connection failed: {e}")

# Disable tracing since we're using MLFlow
set_tracing_disabled(disabled=True)

# Load env vars for azure, openai
from agent_hackathon.utils.config import settings

@cl.on_chat_start
async def start():
    """
    Initializes the chat session.
    Stores the agent and an empty conversation history in the user session.
    """
    cl.user_session.set("agent", main_agent)
    cl.user_session.set("conversation", [])

@cl.on_message
async def main(message: cl.Message):
    try:
        full_conversation: list[TResponseInputItem] = cl.user_session.get("conversation", [])
        full_conversation.append({"role": "user", "content": message.content})
        agent: Agent = cl.user_session.get("agent", main_agent)
        # Send user request to agent and show result
        result = await Runner.run(
            starting_agent=agent,
            input=full_conversation,
            context={},
            max_turns=20,
        )

        await cl.Message(
            content=result.final_output, author=result.last_agent.name
        ).send()

        full_conversation = result.to_input_list()
        cl.user_session.set("conversation", full_conversation)
        # If handoff occured, set agent to new agent
        cl.user_session.set("agent", result.last_agent)

        # TODO(task Bonus): implement handoff to human

    except OpenAIError as e:
        message = f"OpenAI API Error: {e}"
        logger.error(message)
        await cl.ErrorMessage(content = message).send()
    except AuthenticationError as e:
        message = f"Azure OpenAI Authentication Error: {e}"
        logger.error(message)
        await cl.ErrorMessage(content = message).send()
    except Exception as e:
        message = f"An unexpected error occurred: {e}"
        logger.error(message)
        await cl.ErrorMessage(content = message).send()

    # Send a response back to the user

if __name__ == "__main__":
    from chainlit.cli import run_chainlit
    run_chainlit(__file__)