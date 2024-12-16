from threading import Lock
from datetime import datetime, timedelta
import threading
from typing import Optional, Dict
from contextlib import contextmanager
import weakref

class ConnectionManager:
    def __init__(self, timeout_seconds: int = 20):
        self._connections: Dict[int, tuple[AzureOpenAI, datetime]] = {}
        self._lock = Lock()
        self._timeout_seconds = timeout_seconds
        self._cleanup_thread = threading.Thread(target=self._cleanup_old_connections, daemon=True)
        self._cleanup_thread.start()
    
    def _cleanup_old_connections(self):
        while True:
            with self._lock:
                current_time = datetime.now()
                sessions_to_remove = []
                
                for session_id, (client, last_used) in self._connections.items():
                    if (current_time - last_used).total_seconds() > self._timeout_seconds:
                        client.close()
                        sessions_to_remove.append(session_id)
                
                for session_id in sessions_to_remove:
                    del self._connections[session_id]
            
            threading.Event().wait(1)  # Check every second

    def get_connection(self) -> AzureOpenAI:
        session_id = threading.get_ident()
        
        with self._lock:
            if session_id in self._connections:
                client, _ = self._connections[session_id]
                self._connections[session_id] = (client, datetime.now())
                return client
            
            new_client = AzureOpenAI(
                api_key=os.getenv("AZURE_OPENAI_KEY"),
                api_version="2024-02-01",
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
            )
            self._connections[session_id] = (new_client, datetime.now())
            return new_client

    def close_connection(self, session_id: Optional[int] = None):
        if session_id is None:
            session_id = threading.get_ident()
        
        with self._lock:
            if session_id in self._connections:
                client, _ = self._connections[session_id]
                client.close()
                del self._connections[session_id]

class AzureOpenAIClient:
    _connection_manager = ConnectionManager()

    @property
    def CLIENT(self) -> AzureOpenAI:
        return self._connection_manager.get_connection()

    def __del__(self):
        self._connection_manager.close_connection()

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
    SYS_PROMPT = '"""""Help the user find the answer they are looking for.""""'

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
                {"role": "user", "content": user_query}
            ]
        )
        return response.choices[0].message.content

if __name__ == "__main__":
    # Example usage
    llm = AzureOpenAIChat()
    print(llm.generate_response("Give me summary of all the issues in August this year. Give 1 point."))

    encoder = AzureOpenAIEmbeddings()
    # No need to explicitly close - the connection manager handles this
