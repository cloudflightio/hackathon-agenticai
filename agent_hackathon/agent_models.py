# agent_models.py

from agents import Agent, ModelSettings, OpenAIChatCompletionsModel
# from agents.extensions.models.litellm_model import LitellmModel

from openai import AsyncAzureOpenAI
from agent_hackathon.agent_system_prompts import (
    get_coordination_agent,
    get_account_billing_agent_prompt,
    get_product_support_agent_prompt,
    get_order_management_agent_prompt
)

from agent_hackathon.utils.config import settings

# Create the Async Azure OpenAI client
azure_client = AsyncAzureOpenAI(
    api_key=settings.azure_openai_key,
    api_version=settings.azure_openai_api_version,
    azure_endpoint=settings.azure_openai_endpoint,
)

def _azure_model(deployment_env_var: str) -> OpenAIChatCompletionsModel:
    return OpenAIChatCompletionsModel(
        model          = deployment_env_var,
        openai_client  = azure_client,
    )

model_definition = _azure_model(settings.azure_openai_gpt_deployment)

# LiteLLM model definition (for providers other than Azure AI Foundry)

# model = "gemini/gemini-2.0-flash"
# model = "anthropic/claude-3-5-sonnet-20240620"
# model_definition = LitellmModel(model=model, api_key=api_key)

account_billing_agent = Agent(
    name="AccountBillingAgent",
    instructions=get_account_billing_agent_prompt(),
    # TODO(task 4): add tools to read database and answer questions
    tools=[],
    model=model_definition,
    output_type=None
)

product_support_agent = Agent(
    name="ProductSupportAgent",
    instructions=get_product_support_agent_prompt(),
    # TODO(task 4): add tools to read database and answer questions
    tools=[],
    model=model_definition,
    output_type=None
)

order_management_agent = Agent(
    name="OrderManagementAgent",
    instructions=get_order_management_agent_prompt(),
    # TODO(task 4): add tools to read database and answer questions
    tools=[],
    model=model_definition,
    output_type=None
)

main_agent = Agent(
    name="CustomerSupportCoordinator",
    instructions=get_coordination_agent(),
    # TODO(task 1): add handoffs
    handoffs=[],
    model=model_definition,
    model_settings=ModelSettings(
        temperature=0.7,
    ),
    output_type=None
)

# TODO(task 1): Handoff back to the main agent to process complex requests