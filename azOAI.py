from time import time
from typing import Optional
from openai import AzureOpenAI
from openai import APIError, APIConnectionError, RateLimitError
from threading import Lock
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
import logging
import os

logger = logging.getLogger(__name__)

class ManagedAzureOpenAIClient:
    def __init__(self, connection_timeout: int = 20):
        self._client: Optional[AzureOpenAI] = None
        self._creation_time: Optional[float] = None
        self._connection_timeout = connection_timeout
        self._lock = Lock()
        self._create_client()  # Initialize client immediately

    def _create_client(self):
        """Create a new Azure OpenAI client"""
        self._client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            api_version="2024-02-01",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        self._creation_time = time()
        logger.info("Created new Azure OpenAI client connection")

    @property
    def client(self) -> AzureOpenAI:
        with self._lock:
            current_time = time()
            
            # Check if we need to recreate the client
            if (self._client is None or 
                self._creation_time is None or 
                (current_time - self._creation_time) > self._connection_timeout):
                
                # Close existing client if it exists
                self.close()
                
                # Create new client
                self._create_client()

            return self._client

    def close(self):
        """Close the current connection"""
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
        self._managed_client = ManagedAzureOpenAIClient(connection_timeout=20)

    @property
    def client(self) -> AzureOpenAI:
        return self._managed_client.client

    def close(self):
        if hasattr(self, '_managed_client'):
            self._managed_client.close()

    def __del__(self):
        self.close()

class AzureOpenAIEmbeddings(EmbeddingFunction, AzureOpenAIClient):
    def __init__(self):
        super().__init__()
        
    def get_embeddings(self, texts):
        response = self.client.embeddings.create(
            input=texts, 
            model=config.model_embedding
        )
        return [data.embedding for data in response.data]

    @retry(
        wait=wait_exponential(multiplier=1, min=4, max=10),
        stop=stop_after_attempt(5),
        retry=retry_if_exception_type((APIError, APIConnectionError, RateLimitError))
    )
    def get_embeddings_with_retry(self, texts):
        try:
            return self.get_embeddings(texts)
        except (APIError, APIConnectionError, RateLimitError) as e:
            logger.error(f"Retryable error in embeddings: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Non-retryable error in embeddings: {str(e)}")
            raise

    def __call__(self, texts):
        if isinstance(texts, str):
            texts = [texts]
        return self.get_embeddings_with_retry(texts)

class AzureOpenAIChat(AzureOpenAIClient):
    def __init__(self):
        super().__init__()
        self.SYS_PROMPT = '"""""Help the user find the answer they are looking for.""""'

    def generate_response(self, user_query):
        response = self.client.chat.completions.create(
            model=config.model_chat,
            max_tokens=4096,
            temperature=0.1,
            messages=[
                {"role": "system", "content": self.SYS_PROMPT},
                {"role": "user", "content": user_query},
            ]
        )
        return response.choices[0].message.content

    @retry(
        wait=wait_exponential(multiplier=1, min=4, max=10),
        stop=stop_after_attempt(5),
        retry=retry_if_exception_type((APIError, APIConnectionError, RateLimitError))
    )
    def generate_response_with_retry(self, user_query):
        try:
            return self.generate_response(user_query)
        except (APIError, APIConnectionError, RateLimitError) as e:
            logger.error(f"Retryable error in chat: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Non-retryable error in chat: {str(e)}")
            raise

def main():
    llm = None
    encoder = None
    
    try:
        # Test chat
        llm = AzureOpenAIChat()
        response = llm.generate_response_with_retry(
            "Give me summary of all the issues in August this year. Give 1 point."
        )
        print(f"\nResponse: {response}")

        # Test embeddings
        encoder = AzureOpenAIEmbeddings()
        embeddings = encoder(["Test embedding"])
        print("\nEmbeddings generated successfully")
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        raise
    finally:
        # Clean up resources
        if llm:
            llm.close()
        if encoder:
            encoder.close()

if __name__ == "__main__":
    main()
