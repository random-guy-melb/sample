from sentence_transformers import CrossEncoder
import numpy as np
from Levenshtein import distance as levenshtein_distance

def sigmoid(x):
    """Compute sigmoid values for each set of scores in x."""
    return 1 / (1 + np.exp(-x))

def normalize_scores(scores):
    """Normalize scores using standardization and sigmoid function."""
    mean = np.mean(scores)
    std = np.std(scores)
    if std == 0:
        std = 1e-8  # Avoid division by zero
    standardized = (scores - mean) / std
    return sigmoid(standardized)

def levenshtein_similarity(s1, s2):
    """Convert Levenshtein distance to a similarity score."""
    max_len = max(len(s1), len(s2))
    return 1 - levenshtein_distance(s1, s2) / max_len

def hybrid_score(semantic_score, levenshtein_score, alpha=0.7):
    """Combine semantic and Levenshtein scores."""
    return alpha * semantic_score + (1 - alpha) * levenshtein_score

# Load the model
model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

# Example query and documents
query = "Who wrote 'To Kill a Mockingbird'?"
documents = [
    "The novel 'Moby-Dick' was written by Herman Melville and first published in 1851. It is considered a masterpiece of American literature and deals with complex themes of obsession, revenge, and the conflict between good and evil.",
    "Harper Lee, an American novelist widely known for her novel 'To Kill a Mockingbird', was born in 1926 in Monroeville, Alabama. She received the Pulitzer Prize for Fiction in 1961.",
    "Jane Austen was an English novelist known primarily for her six major novels, which interpret, critique and comment upon the British landed gentry at the end of the 18th century.",
    "'To Kill a Mockingbird' is a novel by Harper Lee published in 1960. It was immediately successful, winning the Pulitzer Prize, and has become a classic of modern American literature.",
    "The 'Harry Potter' series, which consists of seven fantasy novels written by British author J.K. Rowling, is among the most popular and critically acclaimed books of the modern era.",
    "'The Great Gatsby', a novel written by American author F. Scott Fitzgerald, was published in 1925. The story is set in the Jazz Age and follows the life of millionaire Jay Gatsby and his pursuit of Daisy Buchanan."
]

# Get the semantic scores
semantic_scores = model.predict([(query, doc) for doc in documents])

# Normalize semantic scores
normalized_semantic_scores = normalize_scores(semantic_scores)

# Calculate Levenshtein similarities
levenshtein_scores = [levenshtein_similarity(query, doc) for doc in documents]

# Combine scores
hybrid_scores = [hybrid_score(sem_score, lev_score) 
                 for sem_score, lev_score in zip(normalized_semantic_scores, levenshtein_scores)]

# Create a list of tuples with (document_id, hybrid_score, semantic_score, levenshtein_score, document)
results = list(enumerate(zip(hybrid_scores, normalized_semantic_scores, levenshtein_scores, documents)))

# Sort the results by hybrid score in descending order
results.sort(key=lambda x: x[1][0], reverse=True)

# Print the results
for doc_id, (hybrid_score, semantic_score, levenshtein_score, document) in results:
    print(f"Document ID: {doc_id}")
    print(f"Hybrid Score: {hybrid_score:.4f}")
    print(f"Semantic Score: {semantic_score:.4f}")
    print(f"Levenshtein Score: {levenshtein_score:.4f}")
    print(f"Document: {document}")
    print()
