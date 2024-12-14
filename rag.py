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


class RAGApplication(DataProcessing):

    def __init__(self, index_dir: str = "whoosh_index",
                 chroma_persist_directory: str = "chroma_db",
                 embeddings_model=None):
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

        self.chroma_collection = self.chroma_client.get_or_create_collection(
            "coles",
            embedding_function=embeddings_model,
            metadata={"hnsx:space": "cosine"})

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

    def add_document(self,
                     doc_id: Union[str, List[str]],
                     content: Union[str, List[str]],
                     timestamp: Union[datetime.timestamp, List[datetime.timestamp]],
                     category: Union[str, List[str]] = "NA",
                     escalated: Union[bool, List[bool]] = False,
                     resolved: Union[bool, List[bool]] = False,
                     project: Union[str, List[str]] = "NA",
                     groupID: Union[str, List[str]] = "NA",
                     custom_metadata: Union[dict, List[dict]] = None):

        # Convert single inputs to lists for batch processing
        is_batch = isinstance(doc_id, list)
        doc_ids = doc_id if is_batch else [doc_id]
        contents = content if is_batch else [content]
        timestamps = timestamp if is_batch else [timestamp]
        categories = category if isinstance(category, list) else [category] * len(doc_ids)
        escalated_list = escalated if isinstance(escalated, list) else [escalated] * len(doc_ids)
        resolved_list = resolved if isinstance(resolved, list) else [resolved] * len(doc_ids)
        projects = project if isinstance(project, list) else [project] * len(doc_ids)
        groupIDs = groupID if isinstance(groupID, list) else [groupID] * len(doc_ids)
        metadata_list = custom_metadata if isinstance(custom_metadata, list) else [custom_metadata] * len(doc_ids)

        # Process Whoosh updates
        writer = self.whoosh_index.writer()

        with self.whoosh_index.searcher() as searcher:
            for doc_id, content, ts in zip(doc_ids, contents, timestamps):
                existing_doc = searcher.document(id=doc_id)
                if existing_doc:
                    writer.update_document(
                        id=doc_id,
                        content=content,
                        timestamp=datetime.fromtimestamp(ts)
                    )
                else:
                    writer.add_document(
                        id=doc_id,
                        content=content,
                        timestamp=datetime.fromtimestamp(ts)
                    )
        writer.commit()

        # Process Chroma updates
        if not any(custom_metadata):
            # Create default metadata for each document
            metadatas = [
                {
                    "id": d_id,
                    "timestamp": ts,
                    "category": cat,
                    "escalated": esc,
                    "resolved": res,
                    "project": proj,
                    "groupID": grp
                }
                for d_id, ts, cat, esc, res, proj, grp in zip(
                    doc_ids, timestamps, categories, escalated_list,
                    resolved_list, projects, groupIDs
                )
            ]
        else:
            metadatas = [meta for meta in metadata_list if meta is not None]

        # Batch upsert to Chroma
        self.chroma_collection.upsert(
            documents=contents,
            metadatas=metadatas,
            ids=doc_ids
        )

    def get_min_max_date(self):
        result = self.chroma_collection.get(where={})
        if result["metadatas"]:
            timestamps = self.sort_ts(self.get_ts(result))
            return timestamps[0], timestamps[-1]
        return None

    def filter_chroma_results(self, data, threshold=.35):
        try:
            print(data['distances'][0])
            return [data['documents'][0][idx] for idx, val in enumerate(data['distances'][0]) if val <= threshold]
        except:
            docs = data["documents"]
            ts = self.get_ts(data)
            combined_data = list(zip(docs, ts))
            return [record[0] for record in sorted(combined_data, key=lambda x: x[1])]

    def match_record(self, keywords, record, counter, month_keys, value):
        flag = False
        for keyword in keywords:
            date = self.parse_record(record)["Date"]
            try:
                month = self.get_record_by_month(self.date_to_timestamp(date))
            except:
                month = self.get_record_by_month(self.date_to_timestamp(date.split("|")[0].strip()))
            for key in month_keys:
                if month.lower() in key.lower():
                    month_key = key
                    break
            target = self.parse_record(record)[value]
            score = self.levenshtein_similarity(keyword.lower(), target.lower())
            if score > .85:
                counter[keyword]["total_count"] += 1
            try:
                counter[keyword]["monthly_count"][month_key] += 1
            except:
                counter[keyword]["monthly_count"][month_key] = 1
            flag = True

            if value != "GroupID":
                return flag
            else:
                break
        return flag

    def enhance_results(self, encoder, query, docs, alpha):
        # Get the semantic scores
        semantic_scores = encoder.model.predict([(query, doc) for doc in docs])

        # Normalize semantic scores
        normalized_semantic_scores = self.normalize_scores(semantic_scores)

        # Calculate Levenshtein similarities
        levenshtein_scores = [self.levenshtein_similarity(query, doc) for doc in docs]

        # Combine scores
        hybrid_scores = [self.hybrid_score(sem_score, lev_score, alpha=alpha)
                         for sem_score, lev_score in zip(normalized_semantic_scores, levenshtein_scores)]

        # Create a list of tuples with (document_id, hybrid_score, semantic_score, levenshtein_score, document)
        results = list(enumerate(zip(hybrid_scores, normalized_semantic_scores, levenshtein_scores, docs)))

        # Sort the results by hybrid score in descending order
        results.sort(key=lambda x: x[1][0], reverse=True)

        return results

    def sigmoid(self, x):
        """Compute sigmoid values for each set of scores in x."""
        return 1 / (1 + np.exp(-x))

    def normalize_scores(self, scores):
        """Normalize scores using standardization and sigmoid function."""
        mean = np.mean(scores)
        std = np.std(scores)
        if std == 0:
            std = 1e-8  # Avoid division by zero
        standardized = (scores - mean) / std
        return self.sigmoid(standardized)

    def levenshtein_similarity(self, s1, s2):
        """Convert Levenshtein distance to a similarity score."""
        max_len = max(len(s1), len(s2))
        return 1 - levenshtein_distance(s1, s2) / max_len

    def hybrid_score(self, semantic_score, levenshtein_score, alpha=0.7):
        """Combine semantic and Levenshtein scores."""
        return alpha * semantic_score + (1 - alpha) * levenshtein_score

    def search(self,
               query: Optional[str] = None,
               start_date: Optional[datetime.timestamp] = None,
               end_date: Optional[datetime.timestamp] = None,
               bm_percentile: Optional[float] = .9,
               vector_match_threshold: Optional[float] = .2,
               clause: Optional[dict] = None,
               top_k: int = None) -> tuple:
        with self.whoosh_index.searcher() as searcher:
            if query:
                query_parser = QueryParser("content", self.whoosh_index.schema)
                content_query = query_parser.parse(query)
            else:
                content_query = Every()

            if start_date and end_date:
                date_range = DateRange("timestamp",
                                       datetime.fromtimestamp(start_date),
                                       datetime.fromtimestamp(end_date))
                final_query = content_query & date_range
            else:
                final_query = content_query

            whoosh_results = searcher.search(final_query, limit=None)
            scores = [hit.score for hit in whoosh_results]
            if int(sum(scores)) > len(whoosh_results):
                threshold = np.percentile(scores, bm_percentile * 100)
                whoosh_content = [hit['content'] for hit in whoosh_results if hit.score > threshold]
            else:
                whoosh_content = []


            if not clause:
                where_clause = {}
                if start_date and end_date:
                    where_clause = {
                        "$and": [
                            {"timestamp": {"$gte": start_date}},
                            {"timestamp": {"$lte": end_date}}
                        ]
                    }
            else:
                where_clause = clause

            if query:
                chroma_results = self.chroma_collection.query(
                    query_texts=[query],
                    where=where_clause if where_clause else None,
                    n_results=top_k
                )
            else:
                chroma_results = self.chroma_collection.get(
                    where=where_clause if where_clause else None
                )

            chroma_content = self.filter_chroma_results(chroma_results, vector_match_threshold)
            results = list(dict.fromkeys(chroma_content + whoosh_content))

            return whoosh_results, chroma_results, results



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
