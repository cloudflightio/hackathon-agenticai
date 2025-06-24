
from openai import AzureOpenAI
from agent_hackathon.utils.config import settings

class Embedder:
    def __init__(self):
        self.embedder = AzureOpenAI(
            azure_deployment=settings.azure_openai_embedding_deployment,
            api_version=settings.azure_openai_api_version_embedding,
            azure_endpoint=settings.azure_openai_endpoint_embedding,
            api_key=settings.azure_openai_key_embedding,
        )


    def embed_string(self, string: str) -> list[float]:
        """Embed the given text and return the vector."""
        embedding_response = self.embedder.embeddings.create(
            input=string, model=settings.azure_openai_embedding_model_name
        )
        return embedding_response.data[0].embedding