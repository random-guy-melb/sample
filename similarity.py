from sentence_transformers import CrossEncoder
import numpy as np

def normalize_scores(scores):
    """Normalize scores using log transformation and min-max scaling."""
    # Add a small constant to avoid log(0)
    log_scores = np.log(scores - np.min(scores) + 1e-10)
    
    # Apply min-max scaling to bring scores to [0, 1] range
    normalized = (log_scores - np.min(log_scores)) / (np.max(log_scores) - np.min(log_scores))
    
    return normalized

# Load the model, here we use our base sized model
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

# Get the scores
scores = model.predict([(query, doc) for doc in documents])

# Apply our custom normalization
normalized_scores = normalize_scores(scores)

# Create a list of tuples with (document_id, normalized_score, document)
results = list(enumerate(zip(normalized_scores, documents)))

# Sort the results by score in descending order
results.sort(key=lambda x: x[1][0], reverse=True)

# Print the results
for doc_id, (score, document) in results:
    print(f"Document ID: {doc_id}")
    print(f"Score: {score:.4f}")
    print(f"Document: {document}")
    print()
