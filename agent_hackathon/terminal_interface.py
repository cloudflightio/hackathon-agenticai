# main.py
import mlflow
import asyncio
from agent_hackathon.utils.settings import ENVSettings
from agent_hackathon.agent_models import main_agent
from agent_hackathon.utils.debug_agent import log_intermediate_agent_results
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

import asyncio
from agents import Agent, Runner
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
settings = ENVSettings()

async def main():
    agent = main_agent
    with mlflow.start_run():
        try:
            # conversation history needs to be tracked
            full_conversation: list[TResponseInputItem] = []
            cycle_counter = 0
            print("\n=== ElectroStore Customer support ===")
            print("How can we assist you today? \n")
            while True:
                # Print welcome message and help
                print("\nType 'quit', 'exit', or 'c' to exit")
                user_input = input("User input: ").strip()

                if user_input.lower() in {"quit", "exit", "c"}:
                    logger.info("Exiting by command!")
                    break

                full_conversation.append({"role": "user", "content": user_input})

                # Send user request to agent and show result
                result = await Runner.run(
                    starting_agent=agent,
                    input=full_conversation,
                    context={},
                    max_turns=20,
                )
                logger.info(f"Agent reply: {result.final_output}")

                full_conversation = result.to_input_list()
                agent = result.last_agent

                # TODO(task Bonus): implement handoff to human
                # Only for debugging / developing:
                log_intermediate_agent_results(result, cycle_counter)

                full_conversation = result.to_input_list()
                cycle_counter += 1
                # TODO(task Bonus): implement handoff to human

        except OpenAIError as e:
            logger.error(f"OpenAI API Error: {e}")
        except AuthenticationError as e:
            logger.error(f"Azure OpenAI Authentication Error: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(main())
