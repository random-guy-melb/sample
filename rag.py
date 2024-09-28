import os
import shutil
from typing import List, Optional
from datetime import datetime
from whoosh import index
from whoosh.fields import Schema, TEXT, ID, DATETIME
from whoosh.qparser import QueryParser
from whoosh.query import DateRange, Every
import chromadb
from chromadb.config import Settings, DEFAULT_TENANT, DEFAULT_DATABASE
from sentence_transformers import SentenceTransformer
from gensim.models import KeyedVectors
import nltk
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize

nltk.download('punkt')
nltk.download('wordnet')

class MyEmbeddingFunction(chromadb.EmbeddingFunction):
    _MODEL = SentenceTransformer('all-MiniLM-L6-v2', device='mps', trust_remote_code=True)

    def __call__(self, input: chromadb.Documents) -> chromadb.Embeddings:
        embeddings = self._MODEL.encode(input)
        embeddings_as_list = [embedding.tolist() for embedding in embeddings]
        return embeddings_as_list

class RAGApplication:
    def __init__(self, index_dir: str = "whoosh_index", chroma_persist_directory: str = "chroma_db", word2vec_model_path: str = "path_to_word2vec_model.bin"):
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
        self.word2vec_model = KeyedVectors.load_word2vec_format(word2vec_model_path, binary=True)

    # ... (other methods remain the same)

    def enhance_query(self, query: str, num_expansions: int = 2) -> str:
        tokens = word_tokenize(query.lower())
        expanded_query = []

        for token in tokens:
            expanded_query.append(token)
            
            # Add synonyms from WordNet
            synsets = wordnet.synsets(token)
            wordnet_synonyms = set()
            for synset in synsets:
                for lemma in synset.lemmas():
                    if lemma.name() != token:
                        wordnet_synonyms.add(lemma.name().replace('_', ' '))
            
            # Add similar words from Word2Vec
            try:
                similar_words = self.word2vec_model.most_similar(token, topn=num_expansions)
                word2vec_expansions = [word for word, _ in similar_words]
            except KeyError:
                word2vec_expansions = []
            
            # Combine and add expansions
            expansions = list(wordnet_synonyms)[:num_expansions] + word2vec_expansions[:num_expansions]
            expanded_query.extend(expansions)

        return ' OR '.join(expanded_query)

    def search(self, query: Optional[str] = None, start_date: Optional[datetime] = None, 
               end_date: Optional[datetime] = None, top_k: int = 5, 
               bm25_threshold: float = 0.0, chroma_threshold: float = 0.0) -> List[dict]:
        
        whoosh_ids = []
        chroma_ids = []

        # Enhance the query
        enhanced_query = self.enhance_query(query) if query else None

        # BM25 search using Whoosh
        with self.whoosh_index.searcher() as searcher:
            if enhanced_query:
                query_parser = QueryParser("content", self.whoosh_index.schema)
                content_query = query_parser.parse(enhanced_query)
            else:
                content_query = Every()  # Matches all documents

            if start_date and end_date:
                date_range = DateRange("timestamp", start_date, end_date)
                final_query = content_query & date_range
            else:
                final_query = content_query

            whoosh_results = searcher.search(final_query, limit=top_k)
            whoosh_ids = [hit['id'] for hit in whoosh_results if hit.score > bm25_threshold]

        # Vector search using ChromaDB
        where_clause = {}
        if start_date and end_date:
            where_clause = {
                "$and": [
                    {"timestamp": {"$gte": start_date.timestamp()}},
                    {"timestamp": {"$lte": end_date.timestamp()}}
                ]
            }

        if query:
            chroma_results = self.chroma_collection.query(
                query_texts=[query],  # Use original query for vector search
                where=where_clause if where_clause else None,
                n_results=top_k
            )
            # Filter ChromaDB results based on the threshold
            chroma_ids = [id for id, score in zip(chroma_results['ids'][0], chroma_results['distances'][0]) 
                          if score > chroma_threshold]
        else:
            # If no query is provided, fetch all documents within the date range
            chroma_results = self.chroma_collection.get(
                where=where_clause if where_clause else None,
                limit=top_k
            )
            chroma_ids = chroma_results['ids']

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
    rag = RAGApplication(index_dir="/rag/db", 
                         word2vec_model_path="path_to_word2vec_model.bin")

    # Add some sample documents with timestamps
    rag.add_document("1", "Python is a high-level programming language.", datetime(2023, 1, 1))
    rag.add_document("2", "Machine learning is a subset of artificial intelligence.", datetime(2023, 4, 15))
    rag.add_document("3",
                     "Natural language processing deals with the interaction between computers and humans using natural language.",
                     datetime(2023, 3, 1))

    # Perform a search with date range
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 3, 1)

    # Perform a search with query enhancement
    results = rag.search("programming languages", 
                         start_date=start_date, 
                         end_date=end_date, 
                         top_k=5, 
                         bm25_threshold=0.5, 
                         chroma_threshold=0.7)

    print("Search results with query enhancement:")
    for result in results:
        print(f"ID: {result['id']}")
        print(f"Content: {result['content']}")
        print(f"Timestamp: {result['timestamp']}")
        print(f"Source: {result['source']}")
        print("---")

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
