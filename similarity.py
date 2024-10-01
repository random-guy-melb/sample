from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch
from typing import List, Tuple
import numpy as np


def load_model_and_tokenizer():
    """Load the pre-trained cross-encoder model and tokenizer."""
    model_name = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    return model, tokenizer


def normalize_scores(scores: List[float]) -> List[float]:
    """Normalize scores to a 0-1 range using min-max normalization."""
    min_score = min(scores)
    max_score = max(scores)
    if min_score == max_score:
        return [1.0 for _ in scores]  # All scores are the same
    return [(score - min_score) / (max_score - min_score) for score in scores]


def calculate_similarities(model, tokenizer, input_text: str, options: List[str]) -> List[float]:
    """Calculate normalized similarity scores between input_text and options using the cross-encoder."""
    pairs = [[input_text, option] for option in options]
    features = tokenizer(pairs, padding=True, truncation=True, return_tensors="pt")

    with torch.no_grad():
        scores = model(**features).logits.squeeze().tolist()

    return normalize_scores(scores)


def find_different_options(model, tokenizer, input_text: str, options: List[str], cutoff_score: float) -> List[
    Tuple[str, float]]:
    """Find options that are different from the input text based on a cutoff score."""
    similarities = calculate_similarities(model, tokenizer, input_text, options)
    different_options = [(option, sim) for option, sim in zip(options, similarities) if sim < cutoff_score]
    return different_options


def analyze_text_similarity(input_text: str, options: List[str], cutoff_score: float = 0.5) -> dict:
    """Analyze text similarity and return a dictionary with results."""
    model, tokenizer = load_model_and_tokenizer()
    different_options = find_different_options(model, tokenizer, input_text, options, cutoff_score)

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
