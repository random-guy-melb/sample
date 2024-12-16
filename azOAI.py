from threading import Lock
from datetime import datetime, timedelta
import threading
from typing import Optional, Dict
from contextlib import contextmanager
import weakref
from tenacity import (
    retry,
    wait_exponential,
    stop_after_attempt,
    retry_if_exception_type
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self, timeout_seconds: int = 20):
        self._connections: Dict[int, tuple[AzureOpenAI, datetime]] = {}
        self._lock = Lock()
        self._timeout_seconds = timeout_seconds
        self._cleanup_thread = threading.Thread(target=self._cleanup_old_connections, daemon=True)
        self._cleanup_thread.start()
        logger.info(f"Connection Manager initialized with {timeout_seconds}s timeout")
    
    def _cleanup_old_connections(self):
        while True:
            with self._lock:
                current_time = datetime.now()
                sessions_to_remove = []
                
                for session_id, (client, last_used) in self._connections.items():
                    if (current_time - last_used).total_seconds() > self._timeout_seconds:
                        try:
                            client.close()
                            logger.info(f"Connection closed due to timeout for session {session_id}")
                        except Exception as e:
                            logger.error(f"Error closing connection for session {session_id}: {e}")
                        sessions_to_remove.append(session_id)
                
                for session_id in sessions_to_remove:
                    del self._connections[session_id]
            
            threading.Event().wait(1)

    @retry(
        wait=wait_exponential(multiplier=1, min=4, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((ConnectionError, TimeoutError))
    )
    def get_connection(self) -> AzureOpenAI:
        session_id = threading.get_ident()
        
        with self._lock:
            if session_id in self._connections:
                client, _ = self._connections[session_id]
                self._connections[session_id] = (client, datetime.now())
                logger.debug(f"Reusing existing connection for session {session_id}")
                return client
            
            try:
                logger.info(f"Opening new connection for session {session_id}")
                new_client = AzureOpenAI(
                    api_key=os.getenv("AZURE_OPENAI_KEY"),
                    api_version="2024-02-01",
                    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
                )
                self._connections[session_id] = (new_client, datetime.now())
                return new_client
            except Exception as e:
                logger.error(f"Failed to create Azure OpenAI client for session {session_id}: {e}")
                raise

    def close_connection(self, session_id: Optional[int] = None):
        if session_id is None:
            session_id = threading.get_ident()
        
        with self._lock:
            if session_id in self._connections:
                client, _ = self._connections[session_id]
                try:
                    client.close()
                    logger.info(f"Connection manually closed for session {session_id}")
                except Exception as e:
                    logger.error(f"Error closing connection for session {session_id}: {e}")
                finally:
                    del self._connections[session_id]

class AzureOpenAIClient:
    _connection_manager = ConnectionManager()

    @property
    def CLIENT(self) -> AzureOpenAI:
        return self._connection_manager.get_connection()

    def __del__(self):
        try:
            self._connection_manager.close_connection()
        except Exception as e:
            logger.error(f"Error in __del__: {e}")

class AzureOpenAIEmbeddings(EmbeddingFunction, AzureOpenAIClient):
    @retry(
        wait=wait_exponential(multiplier=1, min=4, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((openai.error.APIError, openai.error.Timeout))
    )
    def get_embeddings(self, texts):
        session_id = threading.get_ident()
        try:
            logger.info(f"Getting embeddings for session {session_id}")
            response = self.CLIENT.embeddings.create(input=texts, model=config.model_embedding)
            embeddings = [data.embedding for data in response.data]
            return embeddings
        except openai.error.InvalidRequestError as e:
            logger.error(f"Invalid request error in session {session_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in get_embeddings for session {session_id}: {e}")
            raise

    def __call__(self, texts):
        if isinstance(texts, str):
            texts = [texts]
        return self.get_embeddings(texts)

class AzureOpenAIChat(AzureOpenAIClient):
    SYS_PROMPT = '"""""Help the user find the answer they are looking for.""""'

    @retry(
        wait=wait_exponential(multiplier=1, min=4, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((openai.error.APIError, openai.error.Timeout))
    )
    def generate_response(self, user_query):
        session_id = threading.get_ident()
        try:
            logger.info(f"Generating response for session {session_id}")
            response = self.CLIENT.chat.completions.create(
                model=config.model_chat,
                max_tokens=4096,
                temperature=0.1,
                messages=[
                    {"role": "system", "content": self.SYS_PROMPT},
                    {"role": "user", "content": user_query}
                ]
            )
            return response.choices[0].message.content
        except openai.error.InvalidRequestError as e:
            logger.error(f"Invalid request error in session {session_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in generate_response for session {session_id}: {e}")
            raise

if __name__ == "__main__":
    # Example usage
    llm = AzureOpenAIChat()
    print(llm.generate_response("Give me summary of all the issues in August this year. Give 1 point."))

    encoder = AzureOpenAIEmbeddings()
