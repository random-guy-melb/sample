from sentence_transformers import SentenceTransformer, util
from typing import List, Tuple

def load_model():
    """Load the pre-trained sentence transformer model."""
    return SentenceTransformer('all-MiniLM-L6-v2')

def calculate_similarities(model, input_text: str, options: List[str]) -> List[float]:
    """Calculate cosine similarities between input_text and options using sentence embeddings."""
    # Encode all sentences
    embeddings = model.encode([input_text] + options)
    
    # Calculate cosine similarity between input_text and each option
    similarities = util.pytorch_cos_sim(embeddings[0], embeddings[1:]).squeeze().tolist()
    return similarities

def find_different_options(model, input_text: str, options: List[str], cutoff_score: float) -> List[Tuple[str, float]]:
    """Find options that are different from the input text based on a cutoff score."""
    similarities = calculate_similarities(model, input_text, options)
    different_options = [(option, sim) for option, sim in zip(options, similarities) if sim < cutoff_score]
    return different_options

def analyze_text_similarity(input_text: str, options: List[str], cutoff_score: float = 0.5) -> dict:
    """Analyze text similarity and return a dictionary with results."""
    model = load_model()
    different_options = find_different_options(model, input_text, options, cutoff_score)
    
    return {
        "input_text": input_text,
        "cutoff_score": cutoff_score,
        "total_options": len(options),
        "different_options": different_options,
        "num_different_options": len(different_options)
    }

# Example usage
if __name__ == "__main__":
    input_text = "The quick brown fox jumps over the lazy dog"
    options = [
        "The quick brown fox jumps over the lazy dog",
        "A fast auburn canine leaps above the indolent hound",
        "The slow green turtle crawls under the busy cat",
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit"
    ]
    
    result = analyze_text_similarity(input_text, options, cutoff_score=0.5)
    
    print(f"Input text: {result['input_text']}")
    print(f"Cutoff score: {result['cutoff_score']}")
    print(f"Total options analyzed: {result['total_options']}")
    print(f"Number of different options: {result['num_different_options']}")
    
    if result['different_options']:
        print("\nDifferent options:")
        for option, similarity in result['different_options']:
            print(f"- {option} (similarity: {similarity:.2f})")
    else:
        print("\nNo options found below the cutoff score.")
