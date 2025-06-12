# settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class ENVSettings(BaseSettings):
    azure_openai_key: str
    # search and embedding
    azure_search_key: str
    azure_search_admin_key: str
    azure_openai_key_embedding: str

    # shared
    azure_openai_endpoint: str
    azure_openai_gpt_deployment: str
    azure_openai_api_version: str

    azure_openai_api_version_embedding: str
    azure_openai_endpoint_embedding: str
    azure_openai_embedding_deployment: str
    azure_openai_embedding_model_name: str

    azure_speech_region: str

    azure_search_endpoint: str
    search_option: str

    model_config = SettingsConfigDict(
        env_file=('.env.shared', '.env'),
        env_file_encoding="utf-8",
    )
