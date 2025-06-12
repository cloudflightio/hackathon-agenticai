# agent_tools.py
# TODO(task 4): add tools to read database for specialized agents
# TODO(task 5): add tools to write database for specialized agents


from typing import Any, List, Optional, Dict
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

@function_tool
def get_customer_orders(customer_id: str) -> Optional[List[Order]]:
    """
    Get all orders for a specific customer.

    Args:
        customer_id: The customer ID to look up orders for

    Returns:
        List of Order objects if customer exists, None if customer not found
    """
    try:
        logger.info(f"Looking up orders for customer: {customer_id}")

        # Verify customer exists first
        customer = db_service.get_customer_by_identifier(customer_id)
        if not customer:
            logger.warning(f"Customer not found: {customer_id}")
            return None

        orders = db_service.get_orders_by_customer(customer_id)
        logger.info(f"Found {len(orders)} orders for customer {customer_id}")

        # Return the Pydantic models directly
        return orders

    except Exception as e:
        logger.error(f"Error retrieving orders for customer {customer_id}: {e}")
        return None


# Product Support Tools
@function_tool
def get_product_info(product_id: str) -> Optional[Product]:
    """
    Get detailed product information by product ID.

    Args:
        product_id: The product ID to look up

    Returns:
        Product object if found, None otherwise
    """
    try:
        logger.info(f"Looking up product: {product_id}")
        product = db_service.get_product_by_id(product_id)

        if product is None:
            logger.warning(f"Product not found: {product_id}")

        return product

    except Exception as e:
        logger.error(f"Error retrieving product {product_id}: {e}")
        return None


@function_tool
def search_products(query: str) -> SearchResult:
    """
    Search for products in the database by name, category, or description.

    Args:
        query: Search query string

    Returns:
        SearchResult containing matching products (empty if no matches)
    """
    try:
        if not query.strip():
            logger.warning("Empty search query provided")
            return SearchResult(
                query=query,
                products=[],
                results_count=0
            )

        logger.info(f"Searching products with query: {query}")
        products = db_service.search_products(query)

        search_result = SearchResult(
            query=query,
            products=products,
            results_count=len(products),
        )

        logger.info(f"Found {search_result.results_count} products for query: {query}")
        return search_result

    except Exception as e:
        logger.error(f"Error searching products with query '{query}': {e}")
        return SearchResult(
            query=query,
            products=[],
            results_count=0
        )

# Customer Account Tools
@function_tool
def get_customer_info(identifier: str) -> Optional[Customer]:
    """
    Get customer information by customer name or email address.

    Args:
        identifier: Customer name or email address

    Returns:
        Customer object if found, None otherwise
    """
    try:
        logger.info(f"Looking up customer: {identifier}")
        customer = db_service.get_customer_by_identifier(identifier)

        if customer is None:
            logger.warning(f"Customer not found: {identifier}")

        return customer

    except Exception as e:
        logger.error(f"Error retrieving customer {identifier}: {e}")
        return None

@function_tool
def update_customer_name_by_id(
    customer_id: str,
    new_name: str
) -> bool:
    """
    Update a customer's name in the database.

    Args:
        customer_id: The customer ID to update
        new_name: The new name for the customer

    Returns:
        True if update was successful, False otherwise
    """
    try:
        if not new_name.strip():
            logger.error("Cannot update customer with empty name")
            return False

        logger.info(f"Updating customer {customer_id} name to: {new_name}")

        # Update customer
        success = db_service.update_customer_name(customer_id, new_name)

        if success:
            logger.info(f"Successfully updated customer {customer_id} name")
        else:
            logger.warning(f"Failed to update customer {customer_id} name")

        return success

    except Exception as e:
        logger.error(f"Error updating customer {customer_id} to {new_name}: {e}")
        return False
