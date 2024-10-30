def extract_sentences(text):
    sentences = []
    lines = text.strip().split('\n')
    buffer = ''

    for line in lines:
        # Append the line to the buffer with a space
        buffer += ' ' + line.strip()
        # Check if '|' is in the line
        if '|' in line:
            # Split the buffer at the last colon after '|'
            if ':' in buffer:
                parts = buffer.rsplit(':', 1)
                if len(parts) == 2:
                    message = parts[1].strip()
                    if message:
                        sentences.append(message)
            # Reset the buffer after processing
            buffer = ''
        else:
            # If '|' is not in the line, continue accumulating
            continue

    # Handle any remaining text in the buffer
    if buffer.strip():
        sentences.append(buffer.strip())

    return sentences

# Sample data
sample_data = """John Smith | 2024-12-08: Hi how are you?
I am John
Agent | 2024-12-09: Hello John, I am good."""

result = extract_sentences(sample_data)
print(result)
