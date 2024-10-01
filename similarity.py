from typing import List, Tuple
from collections import Counter

def tokenize(text: str) -> List[str]:
    """Convert text to lowercase and split into words."""
    return text.lower().split()

def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate the Jaccard similarity between two texts."""
    words1 = set(tokenize(text1))
    words2 = set(tokenize(text2))
    
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    return intersection / union if union != 0 else 0

def find_different_options(input_text: str, options: List[str], cutoff_score: float) -> List[Tuple[str, float]]:
    """Find options that are different from the input text based on a cutoff score."""
    different_options = []
    for option in options:
        similarity = calculate_similarity(input_text, option)
        if similarity < cutoff_score:
            different_options.append((option, similarity))
    return different_options

def analyze_text_similarity(input_text: str, options: List[str], cutoff_score: float = 0.5) -> dict:
    """Analyze text similarity and return a dictionary with results."""
    different_options = find_different_options(input_text, options, cutoff_score)
    
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
    
    result = analyze_text_similarity(input_text, options, cutoff_score=0.3)
    
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
