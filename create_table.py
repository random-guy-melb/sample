import textwrap


def create_markdown_table(data, columns=None, max_width=20):
    all_headers = ["Serial", "Date", "Category", "Issue", "Resolution", "Context", "Tag"]

    # If no columns are specified, use all headers
    headers = columns if columns else all_headers

    # Ensure all specified columns exist in the data
    headers = [h for h in headers if h in all_headers]

    # Determine the maximum width for each column
    col_widths = {header: min(max_width, max(len(header), max(len(str(row.get(header, ''))) for row in data))) for
                  header in headers}

    def wrap_text(text, width):
        return '\n'.join(textwrap.wrap(str(text), width))

    # Create the separator row
    separator_row = "|" + "|".join('-' * (col_widths[header] + 2) for header in headers) + "|"

    # Create the table
    table = f"{separator_row}\n"  # Add line above column names

    # Create the header row
    header_row = "| " + " | ".join(header.ljust(col_widths[header]) for header in headers) + " |"
    table += f"{header_row}\n{separator_row}\n"

    # Add data rows with separators
    for row in data:
        wrapped_row = [wrap_text(row.get(header, ''), col_widths[header]) for header in headers]
        max_lines = max(len(cell.split('\n')) for cell in wrapped_row)

        for i in range(max_lines):
            line = "| "
            for j, header in enumerate(headers):
                cell_lines = wrapped_row[j].split('\n')
                line += (cell_lines[i] if i < len(cell_lines) else '').ljust(col_widths[header]) + " | "
            table += line + "\n"
        table += separator_row + "\n"  # Add separator after each row

    return table


# Example usage with multiple records
data = [
    {
        "Serial": "4",
        "Date": "14/06/2023 | 1-Jan=2024",
        "Category": "Payment issue",
        "Issue": "Unable to use test credit/debit card in SIT.",
        "Resolution": "ColServices component fixed by development team.",
        "Context": "Arundhati reported svsvsssdvsdbsbsbsdvsdvsdvsdvsvsvssdvsdvsvsvsvsvissue with test cards in SIT. Hariharasudhan mentioned colservices fix. Resolved by DEV team.",
        "Tag": "Escalation, Resolved"
    },
    {
        "Serial": "5",
        "Date": "08/12/2023",
        "Category": "Payment issue",
        "Issue": "Issue when placing order using paypal or card. Insufficient inventory.",
        "Resolution": "Using a different store might help.",
        "Context": "Team facing issue with orders due to insufficient inventory in store 6651. Workaround suggested.",
        "Tag": ""
    },
    # ... (other data entries)
]

# Example usage with all columns
print("Table with all columns:")
all_columns_table = create_markdown_table(data)
print(all_columns_table)

# Example usage with selected columns
print("\nTable with selected columns:")
selected_columns_table = create_markdown_table(data, columns=["Serial", "Date", "Issue"])
print(selected_columns_table)

# Example usage with a single column
print("\nTable with a single column:")
single_column_table = create_markdown_table(data, columns=["Issue"])
print(single_column_table)
