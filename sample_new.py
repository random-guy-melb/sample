import re


def parse_record(text):
    # Define the features we're looking for
    features = [
        "Serial:", "Date:", "Category:", "Issue:", "Resolution:",
        "Context:", "GroupID:", "Tag:"
    ]

    # Create a regular expression pattern
    pattern = "|".join(map(re.escape, features))

    # Split the text, keeping the delimiters
    parts = re.split(f'({pattern})', text)

    # Remove any empty strings and leading/trailing whitespace
    parts = [part.strip() for part in parts if part.strip()]

    # Pair up the features with their values
    result = {}
    for i in range(0, len(parts), 2):
        if i + 1 < len(parts):
            key = parts[i].rstrip(':')
            value = parts[i + 1]
            result[key] = value

    return result


# Example usage:
text_block = ""

parsed_record = parse_record(text_block)
for key, value in parsed_record.items():
    print(f"{key} = {value}")
