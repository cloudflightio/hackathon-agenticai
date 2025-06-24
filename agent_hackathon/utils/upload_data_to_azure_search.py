import json
import os
from typing import List

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes._generated.models import SemanticConfiguration, VectorSearchProfile, SemanticField, \
    SemanticPrioritizedFields, SemanticSearch, ExhaustiveKnnAlgorithmConfiguration, VectorSearch, AzureOpenAIVectorizer, \
    AzureOpenAIVectorizerParameters
from azure.search.documents.indexes.models import (
    ComplexField,
    CorsOptions,
    SearchIndex,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    ScoringProfile, SearchField
)
from openai import AzureOpenAI

from agent_hackathon.utils.embedder import Embedder

# --- Configuration ---
from agent_hackathon.utils.config import settings
service_endpoint = settings.azure_search_endpoint
embedding_endpoint = settings.azure_openai_endpoint_embedding
search_admin_key = settings.azure_search_admin_key

# --- Helper Function to Create Index ---
def create_index_if_not_exists(index_client: SearchIndexClient, index: SearchIndex):
    """
    Creates an Azure Search Index if it doesn't already exist.
    """
    try:
        index_client.get_index(index.name)
        print(f"Index '{index.name}' already exists.")
        return index.name
    except Exception:  # More specific exception could be used if available for "not found"
        try:
            result = index_client.create_index(index)
            print(f"Index '{result.name}' created successfully. ✨")
        except Exception as ex:
            print(f"Error creating index '{index.name}': {ex} 🚨")
        return None


# --- Index Creation Functions ---

def define_products_index() -> SearchIndex:
    """Defines the 'products' Azure Search Index."""
    products_index_name = "products"
    products_fields = [
        SimpleField(name="product_id", type=SearchFieldDataType.String, key=True, sortable=True, filterable=True,
                    facetable=True),
        SearchableField(name="name", type=SearchFieldDataType.String, sortable=True, filterable=True),
        SearchableField(name="category", type=SearchFieldDataType.String, sortable=True, filterable=True,
                        facetable=True),
        SimpleField(name="price", type=SearchFieldDataType.Double, sortable=True, filterable=True, facetable=True),
        SimpleField(name="stock_count", type=SearchFieldDataType.Int32, sortable=True, filterable=True, facetable=True),
        SearchableField(name="description", type=SearchFieldDataType.String, filterable=True),
        SearchField(
            name="embedding",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=1536,
            vector_search_profile_name="exhaustiveKnnProfile",
        ),

    ]
    vector_search = VectorSearch(
        algorithms=[
            ExhaustiveKnnAlgorithmConfiguration(
                name="exhaustiveKnn",
            )
        ],
        vectorizers=[
            AzureOpenAIVectorizer(
                vectorizer_name=f"msft-workshop-{settings.azure_openai_embedding_model_name}",
                parameters=AzureOpenAIVectorizerParameters(
                    resource_url=embedding_endpoint,
                    deployment_name=settings.azure_openai_embedding_model_name,
                    model_name=settings.azure_openai_embedding_model_name
                )
            )
        ],
        profiles=[
            VectorSearchProfile(
                name="exhaustiveKnnProfile",
                algorithm_configuration_name="exhaustiveKnn",
            )
        ],
    )

    # Semantic search configuration
    semantic_config = SemanticConfiguration(
        name="semantic-config",
        prioritized_fields=SemanticPrioritizedFields(
            keywords_fields=[SemanticField(field_name="name"), SemanticField(field_name="category")],
            content_fields=[SemanticField(field_name="description")],
        ),
    )

    semantic_search = SemanticSearch(configurations=[semantic_config])

    products_cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)
    products_scoring_profiles: List[ScoringProfile] = []

    return SearchIndex(
        name=products_index_name,
        fields=products_fields,
        scoring_profiles=products_scoring_profiles,
        cors_options=products_cors_options,
        vector_search=vector_search,
        semantic_search=semantic_search
    )


def define_customers_index() -> SearchIndex:
    """Defines the 'customers' Azure Search Index."""
    customers_index_name = "customers"
    customers_fields = [
        SimpleField(name="customer_id", type=SearchFieldDataType.String, key=True, sortable=True, filterable=True,
                    facetable=True),
        SearchableField(name="name", type=SearchFieldDataType.String, sortable=True, filterable=True),
        SearchableField(name="email", type=SearchFieldDataType.String, filterable=True, sortable=True),
        SimpleField(name="phone", type=SearchFieldDataType.String, filterable=True),
        SearchableField(name="address", type=SearchFieldDataType.String, filterable=True),
    ]
    customers_cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)
    customers_scoring_profiles: List[ScoringProfile] = []

    return SearchIndex(
        name=customers_index_name,
        fields=customers_fields,
        scoring_profiles=customers_scoring_profiles,
        cors_options=customers_cors_options
    )


def define_orders_index() -> SearchIndex:
    """Defines the 'orders' Azure Search Index."""
    orders_index_name = "orders"
    orders_fields = [
        SimpleField(name="order_id", type=SearchFieldDataType.String, key=True, sortable=True, filterable=True,
                    facetable=True),
        SimpleField(name="customer_id", type=SearchFieldDataType.String, filterable=True, facetable=True,
                    sortable=True),
        SearchableField(name="status", type=SearchFieldDataType.String, filterable=True, facetable=True, sortable=True),
        SimpleField(name="total_amount", type=SearchFieldDataType.Double, sortable=True, filterable=True,
                    facetable=True),
        SimpleField(name="order_date", type=SearchFieldDataType.DateTimeOffset, sortable=True, filterable=True,
                    facetable=True),
        SimpleField(name="tracking_number", type=SearchFieldDataType.String, filterable=True),
        ComplexField(
            name="items",
            fields=[
                SimpleField(name="product_id", type=SearchFieldDataType.String, filterable=True, facetable=True),
                SimpleField(name="quantity", type=SearchFieldDataType.Int32, filterable=True, sortable=False),
                SimpleField(name="price", type=SearchFieldDataType.Double, filterable=True, sortable=False),
            ],
            collection=True,
        ),
    ]
    orders_cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)
    orders_scoring_profiles: List[ScoringProfile] = []

    return SearchIndex(
        name=orders_index_name,
        fields=orders_fields,
        scoring_profiles=orders_scoring_profiles,
        cors_options=orders_cors_options
    )


# --- Main Script Logic ---
if __name__ == "__main__":
    if not search_admin_key:
        print("🚨 MAX_AZURE_SEARCH_ADMIN_KEY environment variable is not set.")
        exit(1)

    # Initialize SearchIndexClient
    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(search_admin_key))
    embedder = Embedder()

    # Define and Create Indexes
    print("--- Defining and Creating Indexes ---")
    products_index_definition = define_products_index()
    orders_index_definition = define_orders_index()
    customers_index_definition = define_customers_index()

    created_indices = set()
    for idx_definition in [products_index_definition, customers_index_definition, orders_index_definition]:
        new_index = create_index_if_not_exists(index_client, idx_definition)
        created_indices.add(new_index)

    print("\n--- Index Creation/Verification Complete ---\n")

    # Load data from JSON
    try:
        with open("database.json", "r", encoding='utf-8') as f:
            dataset = json.load(f)
        print("📚 Dataset loaded successfully from database.json.")
    except FileNotFoundError:
        print("🚨 Error: database.json not found. Please ensure the file exists.")
        dataset = {}  # Initialize to empty dict to avoid further errors
    except json.JSONDecodeError:
        print("🚨 Error: Could not decode JSON from database.json. Please check its format.")
        dataset = {}

    # Upload documents to each index
    if dataset:
        print("\n--- Uploading Documents ---")
        for index_name, documents in dataset.items():
            if index_name in created_indices:  # Check if the index exists before uploading
                print(f"Index '{index_name}' already exists. Skipping upload.")
                continue
            if not documents:
                print(f"No documents found for index '{index_name}' in database.json. Skipping upload.")
                continue

            print(f"Uploading documents to '{index_name}' index...")
            try:
                search_client = SearchClient(
                    endpoint=service_endpoint,
                    index_name=index_name,
                    credential=AzureKeyCredential(search_admin_key)
                )
                if index_name == "products":
                    for document in documents:
                        embedding = embedder.embed_string(document["description"])
                        document["embedding"] = embedding

                # The upload_documents method returns a list of IndexingResult objects
                results = search_client.upload_documents(documents=documents)

                successful_uploads = sum(1 for result in results if result.succeeded)
                if successful_uploads == len(documents):
                    print(f"Successfully uploaded {successful_uploads} documents to '{index_name}'. ✅")
                else:
                    print(
                        f"Uploaded {successful_uploads}/{len(documents)} documents to '{index_name}'. Some uploads may have failed.")
                    for i, result in enumerate(results):
                        if not result.succeeded:
                            print(
                                f"  Failed document (original index {i}): ID={documents[i].get('product_id') or documents[i].get('customer_id') or documents[i].get('order_id')}, Error: {result.error_message}")
            except Exception as e:
                print(f"🚨 An error occurred while uploading documents to '{index_name}': {e}")
    else:
        print("No data to upload.")

    print("\n--- Script Finished ---")
