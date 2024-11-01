import re

def extract_dates_and_messages(processed_list):
    date_message_pairs = []
    # Regular expression patterns to match the starting date and colon
    date_patterns = [
        r'^\s*(\d{2}/\d{2}/\d{4})\s*:\s*(.*)',  # MM/DD/YYYY
        r'^\s*(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}(?:\.\d+)?)\s*:\s*(.*)'  # YYYY-MM-DD HH:MM:SS[.microseconds]
    ]
    for line in processed_list:
        date_found = False
        for pattern in date_patterns:
            match = re.match(pattern, line)
            if match:
                date = match.group(1)
                message = match.group(2).strip()
                date_message_pairs.append((date, message))
                date_found = True
                break
        if not date_found:
            # If no date is found, you can decide how to handle it
            date_message_pairs.append((None, line.strip()))
    return date_message_pairs


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
