import os
import shutil
from typing import List
from datetime import datetime
from whoosh import index
from whoosh.fields import Schema, TEXT, ID, DATETIME
from whoosh.qparser import QueryParser
from whoosh.query import DateRange, And
import chromadb
from chromadb.config import Settings, DEFAULT_TENANT, DEFAULT_DATABASE
from sentence_transformers import SentenceTransformer


class MyEmbeddingFunction(chromadb.EmbeddingFunction):
    _MODEL = SentenceTransformer('all-MiniLM-L6-v2', device='mps', trust_remote_code=True)

    def __call__(self, input: chromadb.Documents) -> chromadb.Embeddings:
        embeddings = self._MODEL.encode(input)
        embeddings_as_list = [embedding.tolist() for embedding in embeddings]
        return embeddings_as_list


class RAGApplication:
    def __init__(self, index_dir: str = "whoosh_index", chroma_persist_directory: str = "chroma_db"):
        self.index_dir = index_dir
        self.chroma_persist_directory = chroma_persist_directory
        self.schema = Schema(
            id=ID(stored=True),
            content=TEXT(stored=True),
            timestamp=DATETIME(stored=True)
        )
        self.whoosh_index = self._create_or_load_whoosh_index()
        self.chroma_client = chromadb.PersistentClient(
            path=chroma_persist_directory,
            settings=Settings(),
            tenant=DEFAULT_TENANT,
            database=DEFAULT_DATABASE)
        self.chroma_collection = self.chroma_client.get_or_create_collection("documents",
                                                                             embedding_function=MyEmbeddingFunction(),
                                                                             metadata={"hnsw:space": "cosine"})

    def _create_or_load_whoosh_index(self):
        if not os.path.exists(self.index_dir):
            os.mkdir(self.index_dir)
            return index.create_in(self.index_dir, self.schema)

        try:
            idx = index.open_dir(self.index_dir)
            if idx.schema == self.schema:
                return idx
        except:
            pass

        shutil.rmtree(self.index_dir)
        os.mkdir(self.index_dir)
        return index.create_in(self.index_dir, self.schema)

    def add_document(self, doc_id: str, content: str, timestamp: datetime):
        # Check if document with this id already exists
        with self.whoosh_index.searcher() as searcher:
            existing_doc = searcher.document(id=doc_id)

        writer = self.whoosh_index.writer()
        if existing_doc:
            # Update existing document
            writer.update_document(id=doc_id, content=content, timestamp=timestamp)
        else:
            # Add new document
            writer.add_document(id=doc_id, content=content, timestamp=timestamp)
        writer.commit()

        # Add to ChromaDB
        self.chroma_collection.upsert(
            documents=[content],
            metadatas=[{"id": doc_id, "timestamp": timestamp.timestamp()}],
            ids=[doc_id],
        )

    def search(self, query: str, start_date: datetime = None, end_date: datetime = None, top_k: int = 5) -> List[dict]:
        # BM25 search using Whoosh
        with self.whoosh_index.searcher() as searcher:
            query_parser = QueryParser("content", self.whoosh_index.schema)
            content_query = query_parser.parse(query)

            if start_date and end_date:
                date_range = DateRange("timestamp", start_date, end_date)
                final_query = And([content_query, date_range])
            else:
                final_query = content_query

            whoosh_results = searcher.search(final_query, limit=top_k)
            whoosh_ids = [hit['id'] for hit in whoosh_results]

        # Vector search using ChromaDB
        where_clause = {}
        if start_date and end_date:
            where_clause = {
                "$and": [
                    {"timestamp": {"$gte": start_date.timestamp()}},
                    {"timestamp": {"$lte": end_date.timestamp()}}
                ]
            }

        chroma_results = self.chroma_collection.query(
            query_texts=[query],
            where=where_clause if where_clause else None,
            n_results=top_k
        )
        chroma_ids = chroma_results['ids'][0]

        # Combine and deduplicate results
        combined_ids = list(dict.fromkeys(whoosh_ids + chroma_ids))

        # Fetch full documents
        results = []
        for doc_id in combined_ids[:top_k]:
            with self.whoosh_index.searcher() as searcher:
                whoosh_doc = searcher.document(id=doc_id)
                if whoosh_doc:
                    results.append({
                        "id": doc_id,
                        "content": whoosh_doc['content'],
                        "timestamp": whoosh_doc['timestamp'],
                        "source": "whoosh" if doc_id in whoosh_ids else "chromadb"
                    })

        return results


# Example usage
if __name__ == "__main__":
    rag = RAGApplication(index_dir="/rag/db")

    # Add some sample documents with timestamps
    rag.add_document("1", "Python is a high-level programming language.", datetime(2023, 1, 1))
    rag.add_document("2", "Machine learning is a subset of artificial intelligence.", datetime(2023, 4, 15))
    rag.add_document("3",
                     "Natural language processing deals with the interaction between computers and humans using natural language.",
                     datetime(2023, 3, 1))

    # Perform a search with date range
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 3, 1)
    results_with_date = rag.search("programming languages", start_date, end_date)

    print("Search results with date range:")
    for result in results_with_date:
        print(f"ID: {result['id']}")
        print(f"Content: {result['content']}")
        print(f"Timestamp: {result['timestamp']}")
        print(f"Source: {result['source']}")
        print("---")

    # Perform a search without date range
    results_without_date = rag.search("programming languages")

    print("\nSearch results without date range:")
    for result in results_without_date:
        print(f"ID: {result['id']}")
        print(f"Content: {result['content']}")
        print(f"Timestamp: {result['timestamp']}")
        print(f"Source: {result['source']}")
        print("---")
