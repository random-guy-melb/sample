import re


def process_text(text):
    # Split the text by '|'
    parts = text.split('|')

    # Process each part to remove names but keep dates
    processed_parts = []

    # Regular expressions for date patterns
    date_patterns = [
        r'(?P<date>\d{2}/\d{2}/\d{4})',  # MM/DD/YYYY
        r'(?P<date>\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}(?:\.\d+)?)'  # YYYY-MM-DD HH:MM:SS[.microseconds]
    ]

    for part in parts:
        # Skip empty parts
        if not part.strip():
            continue

        # Replace multiple newlines with space
        part = ' '.join(line.strip() for line in part.splitlines() if line.strip())

        # Find date using regex patterns
        date_found = None
        for pattern in date_patterns:
            match = re.search(pattern, part)
            if match:
                date_found = match.group('date')
                break

        # If date is found, extract the message
        if date_found:
            # Remove the date from the part to get the message
            message = part.replace(date_found, '').strip()
            # Remove any leading colons or spaces
            message = message.lstrip(':').strip()
            processed_line = f"{date_found}: {message}" if message else date_found
            processed_parts.append(processed_line)

    return processed_parts
