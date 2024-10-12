import textwrap
import json
import re


def create_markdown_table(data, columns=None, max_width=50, code_columns=[]):
    all_headers = ["Serial", "Date", "Category", "Issue", "Resolution", "Context", "Tag"]

    headers = columns if columns else all_headers
    headers = [h for h in headers if h in all_headers]

    def is_json(text):
        try:
            json.loads(text)
            return True
        except:
            return False

    def format_code_or_json(text):
        if is_json(text):
            return json.dumps(json.loads(text), indent=2)
        else:
            return textwrap.indent(text.strip(), '  ')

    def process_mixed_content(text, width):
        # Regex to find potential code blocks (indented or between backticks)
        code_pattern = r'(^( {4,}|\t).*$)|(```[\s\S]*?```)'

        parts = re.split(code_pattern, text, flags=re.MULTILINE)
        formatted_parts = []

        for part in parts:
            if part:
                if re.match(code_pattern, part, re.MULTILINE):
                    # This is a code block, preserve its structure
                    formatted_parts.append(format_code_or_json(part))
                else:
                    # This is regular text, wrap it
                    formatted_parts.append('\n'.join(textwrap.wrap(part, width)))

        return '\n'.join(formatted_parts)

    def wrap_text(text, width, is_code_column):
        if is_code_column:
            return process_mixed_content(text, width)
        else:
            return '\n'.join(textwrap.wrap(text, width))

    # Determine the maximum width for each column
    col_widths = {header: max(len(header), min(max_width, max(
        len(line) for row in data for line in str(row.get(header, '')).split('\n')))) for header in headers}

    separator_row = "|" + "|".join('-' * (col_widths[header] + 2) for header in headers) + "|"
    table = f"{separator_row}\n"
    header_row = "| " + " | ".join(header.ljust(col_widths[header]) for header in headers) + " |"
    table += f"{header_row}\n{separator_row}\n"

    for row in data:
        wrapped_row = [wrap_text(str(row.get(header, '')), col_widths[header], header in code_columns).split('\n') for
                       header in headers]
        max_lines = max(len(cell) for cell in wrapped_row)

        for i in range(max_lines):
            line = "| "
            for j, header in enumerate(headers):
                cell_lines = wrapped_row[j]
                cell_content = cell_lines[i] if i < len(cell_lines) else ''
                line += cell_content.ljust(col_widths[header]) + " | "
            table += line + "\n"
        table += separator_row + "\n"

    return table


# Example usage with mixed content
data = [
    {
        "Serial": "1",
        "Date": "15/10/2023",
        "Category": "Mixed content",
        "Issue": "Function not working as expected. Here's the problematic code:\n```python\ndef broken_function(x):\n    return x / 0\n```\nThis causes a division by zero error.",
        "Resolution": "Fixed the function. Here's the corrected version:\n```python\ndef fixed_function(x):\n    if x == 0:\n        return None\n    return 1 / x\n```\nNow it handles the zero case gracefully.",
        "Context": "User reported unexpected crashes. The issue was in the error handling.\nRelated config:\n```json\n{\n  \"error_mode\": \"strict\",\n  \"logging\": true\n}\n```",
        "Tag": "Bug fix, Code update"
    },
    {
        "Serial": "2",
        "Date": "16/10/2023",
        "Category": "Data issue",
        "Issue": "Incorrect JSON structure in config file. Current structure:\n```json\n{\n  \"name\": \"John Doe\"\n  \"age\": 30,\n  \"city\": \"New York\"\n}\n```\nNote the missing comma after \"John Doe\".",
        "Resolution": "Corrected the JSON structure:\n```json\n{\n  \"name\": \"John Doe\",\n  \"age\": 30,\n  \"city\": \"New York\"\n}\n```\nAdded the missing comma.",
        "Context": "This was causing parsing errors in the application. We need to implement better JSON validation in our config loader.",
        "Tag": "Data correction, JSON"
    }
]

# Example usage with all columns, specifying code columns
print("Table with all columns, preserving embedded code and JSON:")
all_columns_table = create_markdown_table(data, code_columns=["Issue", "Resolution", "Context"])
print(all_columns_table)

# Example usage with selected columns
print("\nTable with selected columns:")
selected_columns_table = create_markdown_table(data, columns=["Serial", "Issue", "Resolution"],
                                               code_columns=["Issue", "Resolution"])
print(selected_columns_table)
