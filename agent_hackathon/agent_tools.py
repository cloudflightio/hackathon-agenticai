# agent_tools.py
# TODO(task 4): add tools to read database for specialized agents
# TODO(task 5): add tools to write database for specialized agents


from typing import Optional
from loguru import logger
from agents import function_tool
from agent_hackathon.data_models import (
    Order,
    Customer,
    Product,
    SearchResult
)
from agent_hackathon.utils.database_service import db_service

# NOTE:  the function signature is automatically parsed to extract the schema for the tool,
# and the docstring to extract descriptions for the tool and for individual arguments.
# For more info see: https://openai.github.io/openai-agents-python/tools/#automatic-argument-and-docstring-parsing

# Order Management Tools

# As an example, one tool is already implemented.
@function_tool
def get_order_status(order_id: str) -> Optional[Order]:
    """
    Get order status and details by order ID.

    Args:
        order_id: The order ID to look up

    Returns:
        Order object if found, None otherwise
    """
    try:
        logger.info(f"Looking up order: {order_id}")
        order = db_service.get_order_by_id(order_id)

        if order is None:
            logger.warning(f"Order not found: {order_id}")

        return order

    except Exception as e:
        logger.error(f"Error retrieving order {order_id}: {e}")
        return None