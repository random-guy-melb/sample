from time import time
from typing import Optional
from openai import AzureOpenAI
from threading import Lock
import logging
import os
import weakref

logger = logging.getLogger(__name__)

class ManagedAzureOpenAIClient:
    def __init__(self, connection_timeout: int = 20):
        """
        Initialize the managed Azure OpenAI client with connection timeout in seconds
        """
        self._client: Optional[AzureOpenAI] = None
        self._creation_time: Optional[float] = None
        self._connection_timeout = connection_timeout
        self._lock = Lock()

    @property
    def client(self) -> AzureOpenAI:
        """
        Get the Azure OpenAI client, creating a new one if necessary or if the current one is too old
        """
        with self._lock:
            current_time = time()
            
            # Check if we need to create a new client
            if (
                self._client is None or 
                self._creation_time is None or 
                (current_time - self._creation_time) > self._connection_timeout
            ):
                # Close existing client if it exists
                if self._client is not None:
                    try:
                        self._client.close()
                        logger.info("Closed existing connection due to timeout")
                    except Exception as e:
                        logger.warning(f"Error closing client: {e}")

                # Create new client
                self._client = AzureOpenAI(
                    api_key=os.getenv("AZURE_OPENAI_KEY"),
                    api_version="2024-02-01",
                    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
                )
                self._creation_time = current_time
                logger.info("Created new Azure OpenAI client connection")

            return self._client

    def close(self):
        """
        Explicitly close the current connection
        """
        with self._lock:
            if self._client is not None:
                try:
                    self._client.close()
                    logger.info("Closed connection explicitly")
                except Exception as e:
                    logger.warning(f"Error closing client: {e}")
                finally:
                    self._client = None
                    self._creation_time = None

class AzureOpenAIClient:
    def __init__(self):
        """
        Initialize with a per-instance managed client
        """
        # Each instance gets its own managed client
        self._managed_client = ManagedAzureOpenAIClient(connection_timeout=20)

    @property
    def CLIENT(self) -> AzureOpenAI:
        return self._managed_client.client

    def close(self):
        """
        Close this instance's connection
        """
        self._managed_client.close()

    def __del__(self):
        """
        Ensure connection is closed when the instance is garbage collected
        """
        self.close()

class AzureOpenAIEmbeddings(EmbeddingFunction, AzureOpenAIClient):
    def get_embeddings(self, texts):
        response = self.CLIENT.embeddings.create(input=texts, model=config.model_embedding)
        embeddings = [data.embedding for data in response.data]
        return embeddings

    @retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(5))
    def get_embeddings_with_retry(self, texts):
        try:
            return self.get_embeddings(texts)
        except openai.error.OpenAIError as e:
            logger.error(f"Error fetching embeddings: {e}")
            raise

    def __call__(self, texts):
        if isinstance(texts, str):
            texts = [texts]
        return self.get_embeddings_with_retry(texts)

class AzureOpenAIChat(AzureOpenAIClient):
    def __init__(self):
        super().__init__()
        self.SYS_PROMPT = '"""""Help the user find the answer they are looking for.""""'

    @retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(5))
    def generate_response_with_retry(self, user_query):
        try:
            return self.generate_response(user_query)
        except openai.error.OpenAIError as e:
            logger.error(f"Error fetching response: {e}")
            raise

    def generate_response(self, user_query):
        response = self.CLIENT.chat.completions.create(
            model=config.model_chat,
            max_tokens=4096,
            temperature=0.1,
            messages=[
                {"role": "system", "content": self.SYS_PROMPT},
                {"role": "user", "content": user_query},
            ]
        )
        print("\n")
        return response.choices[0].message.content

if __name__ == "__main__":
    llm = AzureOpenAIChat()
    try:
        llm.SYS_PROMPT = "Help user find what they are looking for."
        print(llm.generate_response("Give me summary of all the issues in August this year. Give 1 point."))

        encoder = AzureOpenAIEmbeddings()
    finally:
        # Close connections for this session
        llm.close()
        encoder.close()
