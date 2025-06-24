# database_service.py
import json
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime, date
from decimal import Decimal
from threading import Lock
from loguru import logger

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery

from agent_hackathon.data_models import Customer, Product, Order, OrderItem
from agent_hackathon.utils.embedder import Embedder

from agent_hackathon.utils.config import settings

class DatabaseService:
    def __init__(self,
                 azure_search_endpoint: str = None,
                 azure_search_index_names: dict[str, str] = None,
                 azure_search_api_key: str = None):
        self.credential = AzureKeyCredential(settings.azure_search_key)
        self.azure_search_endpoint = azure_search_endpoint

        self.products_search_client = SearchClient(endpoint=settings.azure_search_endpoint,
                            index_name="products",
                            credential=self.credential)
        self.customers_search_client = SearchClient(endpoint=settings.azure_search_endpoint,
                            index_name="customers",
                            credential=self.credential)
        self.orders_search_client = SearchClient(endpoint=settings.azure_search_endpoint,
                            index_name="orders",
                            credential=self.credential)
        self.customer_admin_client = SearchClient(endpoint=settings.azure_search_endpoint,
                            index_name="customers",
                            credential=AzureKeyCredential(settings.azure_search_admin_key))

        self.embedder = Embedder()

    def _parse_date(self, date_str: str) -> date:
        """Parse date string to date object."""
        if isinstance(date_str, date):
            return date_str
        return datetime.fromisoformat(date_str).date()

    # Accessors
    def get_order_by_id(self, order_id: str) -> Optional[Order]:
        """Get order by ID and return as Order model."""
        order_data = self.orders_search_client.get_document(key=order_id)
        try:
            order_copy = order_data.copy()

            # Parse and convert data
            order_copy['order_date'] = self._parse_date(order_copy['order_date'])
            order_copy['total_amount'] = Decimal(str(order_copy['total_amount']))

            items = []
            for item_data in order_copy.get('items', []):
                item_copy = item_data.copy()
                item_copy['price'] = Decimal(str(item_copy['price']))
                items.append(OrderItem(**item_copy))
            order_copy['items'] = items
            return Order(**order_data)
        except Exception as e:
            logger.error(f"Error converting order {order_id} to model: {e}")
            return None

    def get_customer_by_identifier(self, identifier: str) -> Optional[Customer]:
        """Get customer by ID, email or name and return as Customer model."""
        customers = self.customers_search_client.search(search_text="*", filter=f"customer_id eq '{identifier}' or email eq '{identifier}' or name eq '{identifier}'")

        customers = list(customers)
        if len(customers) == 0:
            logger.error(f"No customer found for {identifier}")
            return None
        if len(customers) > 1:
            logger.error(f"More than one customer found for {identifier}")
            return None

        logger.info(f"customer found: {customers[0]}")
        try:
            return Customer(**customers[0])
        except Exception as e:
            logger.error(f"Error converting customer {identifier} to model: {e}")
            return None


    def get_product_by_id(self, product_id: str) -> Optional[Product]:
        """Get product by ID and return as Product model."""
        product_data = self.products_search_client.get_document(key=product_id)

        try:
            return Product(**product_data)
        except Exception as e:
            logger.error(f"Error converting product {product_id} to Product model {e}")
            return None

    def get_orders_by_customer(self, customer_id: str) -> List[Order]:
        """Get all orders for a customer and return as list of Order models."""
        raw_orders = self.orders_search_client.search(search_text="*", filter=f"customer_id eq '{customer_id}'")
        orders = []

        for order_data in raw_orders:
            try:
                order_copy = order_data.copy()

                # Parse data
                order_copy['order_date'] = self._parse_date(order_copy['order_date'])
                order_copy['total_amount'] = Decimal(str(order_copy['total_amount']))

                items = []
                for item_data in order_copy.get('items', []):
                    # Convert price to Decimal in each item
                    item_copy = item_data.copy()
                    item_copy['price'] = Decimal(str(item_copy['price']))
                    items.append(OrderItem(**item_copy))
                order_copy['items'] = items

                orders.append(Order(**order_copy))
            except Exception as e:
                logger.error(f"Error converting order to model: {e}")
                # Continue processing other orders

        return orders

    def search_products(self, query: str) -> List[Product]:
        query_embedding = (
            self.embedder.embedder.embeddings.create(input=[query], model=settings.azure_openai_embedding_model_name)
            .data[0]
            .embedding
        )
        vector_query = VectorizedQuery(
            vector=query_embedding,
            k_nearest_neighbors=5,
            fields="embedding",
            exhaustive=True,
        )
        products = self.products_search_client.search(search_text=None, vector_queries=[vector_query])
        results = []

        for product_data in products:
            try:
                results.append(Product(**product_data))
            except Exception as e:
                logger.error(f"Error converting product to model during search: {e}")
                # Continue processing other products

        return results

    # Mutators
    def update_customer_name(self, customer_id: str, new_name: str) -> bool:
        customer = self.customer_admin_client.get_document(key=customer_id)
        try:
            customer['name'] = new_name
            self.customer_admin_client.upload_documents(documents=[customer])
            logger.info(f"Updated customer {customer_id} with name: {new_name}")
            return True
        except Exception as e:
            logger.error(e.message)
            return False

# Create singleton instance
db_service = DatabaseService()