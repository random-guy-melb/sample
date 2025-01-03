

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


from collections import defaultdict
from datetime import datetime
import calendar


def generate_summary_with_date_range(data, start_date=None, end_date=None, categories=None, group_ids=None, tags=None):
    def parse_date(date_str):
        return datetime.strptime(date_str, "%d/%m/%Y")

    def get_date_range_key(date, start, end):
        if date.month == start.month and date.year == start.year:
            return (start, f"{start.strftime('%d-%B-%Y')} to {date.replace(day=calendar.monthrange(date.year, date.month)[1]).strftime('%d-%B-%Y')}")
        elif date.month == end.month and date.year == end.year:
            return (date.replace(day=1), f"{date.replace(day=1).strftime('%d-%B-%Y')} to {end.strftime('%d-%B-%Y')}")
        else:
            return (date.replace(day=1), f"{date.replace(day=1).strftime('%d-%B-%Y')} to {date.replace(day=calendar.monthrange(date.year, date.month)[1]).strftime('%d-%B-%Y')}")

    def split_and_strip(value):
        return [item.strip() for item in value.split(',')] if value else []

    start_date = parse_date(start_date) if start_date else None
    end_date = parse_date(end_date) if end_date else None

    category_count = defaultdict(lambda: {"total": 0, "date_ranges": defaultdict(int)})
    groupid_count = defaultdict(lambda: {"total": 0, "date_ranges": defaultdict(int)})
    tag_count = defaultdict(lambda: {"total": 0, "date_ranges": defaultdict(int)})
    
    category_tag_count = defaultdict(lambda: defaultdict(lambda: {"total": 0, "date_ranges": defaultdict(int)}))
    category_groupid_count = defaultdict(lambda: defaultdict(lambda: {"total": 0, "date_ranges": defaultdict(int)}))
    groupid_tag_count = defaultdict(lambda: defaultdict(lambda: {"total": 0, "date_ranges": defaultdict(int)}))
    
    fields_present = set()

    for row in data:
        date = parse_date(row['Date'])
        if (start_date and date < start_date) or (end_date and date > end_date):
            continue

        sort_key, date_range_key = get_date_range_key(date, start_date, end_date)
        
        category = row.get('Category')
        groupids = split_and_strip(row.get('GroupID', ''))
        row_tags = split_and_strip(row.get('Tag', ''))

        if category:
            fields_present.add('Category')
            if not categories or category in categories:
                category_count[category]["total"] += 1
                category_count[category]["date_ranges"][(sort_key, date_range_key)] += 1
        
        if groupids:
            fields_present.add('GroupID')
            for groupid in groupids:
                if not group_ids or groupid in group_ids:
                    groupid_count[groupid]["total"] += 1
                    groupid_count[groupid]["date_ranges"][(sort_key, date_range_key)] += 1
        
        if row_tags:
            fields_present.add('Tag')
            for tag in row_tags:
                if not tags or tag in tags:
                    tag_count[tag]["total"] += 1
                    tag_count[tag]["date_ranges"][(sort_key, date_range_key)] += 1

        if category and row_tags:
            for tag in row_tags:
                category_tag_count[category][tag]["total"] += 1
                category_tag_count[category][tag]["date_ranges"][(sort_key, date_range_key)] += 1

        if category and groupids:
            for groupid in groupids:
                category_groupid_count[category][groupid]["total"] += 1
                category_groupid_count[category][groupid]["date_ranges"][(sort_key, date_range_key)] += 1

        if groupids and row_tags:
            for groupid in groupids:
                for tag in row_tags:
                    groupid_tag_count[groupid][tag]["total"] += 1
                    groupid_tag_count[groupid][tag]["date_ranges"][(sort_key, date_range_key)] += 1

    summary = []
    
    def format_date_range_count(counts):
        sorted_counts = sorted(counts.items(), key=lambda x: x[0][0])
        return ", ".join([f'"{date_range}": {count}' for (_, date_range), count in sorted_counts])

    def generate_total_summary(count_dict):
        total_records = sum(info["total"] for info in count_dict.values())
        total_date_ranges = defaultdict(int)
        for info in count_dict.values():
            for (sort_key, date_range), count in info["date_ranges"].items():
                total_date_ranges[(sort_key, date_range)] += count
        return total_records, format_date_range_count(total_date_ranges)

    def add_summary_section(title, count_dict, filter_list=None):
        summary.append(f"\n{title}:")
        if title == "Category" and not filter_list:
            total_records, total_date_ranges = generate_total_summary(count_dict)
            summary.append(f"Categories mentioned have combined total number of records: {total_records}, "
                           f"date range wise record count: {total_date_ranges}")
        else:
            if not filter_list:
                for item, info in count_dict.items():
                    summary.append(f'{title}:"{item}" has total number of records: {info["total"]}, '
                                   f'date range wise record count: {format_date_range_count(info["date_ranges"])}')
            else:
                for item in filter_list:
                    info = count_dict.get(item, {"total": 0, "date_ranges": {}})
                    summary.append(f'{title}:"{item}" has total number of records: {info["total"]}, '
                                   f'date range wise record count: {format_date_range_count(info["date_ranges"])}')
            
            total_records, total_date_ranges = generate_total_summary(count_dict)
            summary.append(f"{title}s mentioned have combined total number of records: {total_records}, "
                           f"date range wise record count: {total_date_ranges}")

    # Individual summaries
    if 'Category' in fields_present:
        add_summary_section("Category", category_count, categories)
    if 'GroupID' in fields_present:
        add_summary_section("GroupID", groupid_count, group_ids)
    if 'Tag' in fields_present:
        add_summary_section("Tag", tag_count, tags)

    def add_association_summary(title, count_dict, filter_list1=None, filter_list2=None):
        summary.append(f"\n{title}:")
        total_associations = 0
        total_date_ranges = defaultdict(int)
        if title.startswith("Category-") and not filter_list1:
            for items_dict in count_dict.values():
                for info in items_dict.values():
                    total_associations += info["total"]
                    for (sort_key, date_range), count in info["date_ranges"].items():
                        total_date_ranges[(sort_key, date_range)] += count
        else:
            for item1, items_dict in count_dict.items():
                if not filter_list1 or item1 in filter_list1:
                    summary.append(f'{title.split("-")[0]}:"{item1}" is associated with the following {title.split("-")[1]}s:')
                    for item2, info in items_dict.items():
                        if not filter_list2 or item2 in filter_list2:
                            summary.append(f'  {title.split("-")[1]}:"{item2}" has total number of records: {info["total"]}, '
                                           f'date range wise record count: {format_date_range_count(info["date_ranges"])}')
                            total_associations += info["total"]
                            for (sort_key, date_range), count in info["date_ranges"].items():
                                total_date_ranges[(sort_key, date_range)] += count
        summary.append(f"{title}s have combined total number of records: {total_associations}, "
                       f"date range wise record count: {format_date_range_count(total_date_ranges)}")

    # Category-Tag associations
    if 'Category' in fields_present and 'Tag' in fields_present:
        add_association_summary("Category-Tag", category_tag_count, categories, tags)

    # Category-GroupID associations
    if 'Category' in fields_present and 'GroupID' in fields_present:
        add_association_summary("Category-GroupID", category_groupid_count, categories, group_ids)

    # GroupID-Tag associations
    if 'GroupID' in fields_present and 'Tag' in fields_present:
        add_association_summary("GroupID-Tag", groupid_tag_count, group_ids, tags)

    # Date range info
    date_format = "%d-%B-%Y"
    if start_date and end_date:
        summary.append(f"\nDate range: {start_date.strftime(date_format)} to {end_date.strftime(date_format)}")
    elif start_date:
        summary.append(f"\nDate range: From {start_date.strftime(date_format)}")
    elif end_date:
        summary.append(f"\nDate range: Up to {end_date.strftime(date_format)}")
    else:
        dates = [parse_date(row['Date']) for row in data]
        min_date = min(dates).strftime(date_format)
        max_date = max(dates).strftime(date_format)
        summary.append(f"\nDate range: {min_date} to {max_date}")

    summary.append("All dates are in %d/%m/%Y or %d-%B-%Y format.")

    return "\n".join(summary)


# Example usage
data = [
    {"Serial": "1", "Date": "02/06/2024", "Category": "Access issue", "Tag": "Critical", "GroupID": "Access-Team"},
    {"Serial": "2", "Date": "15/06/2024", "Category": "Payment issue", "Tag": "High-priority", "GroupID": "Payment-Team"},
    {"Serial": "3", "Date": "30/06/2024", "Category": "Access issue", "Tag": "User impact", "GroupID": "Access-Team"},
    {"Serial": "4", "Date": "05/07/2024", "Category": "Payment issue", "Tag": "Financial", "GroupID": "Payment-Team"},
    {"Serial": "5", "Date": "10/07/2024", "Category": "Access issue", "Tag": "Security", "GroupID": "Access-Team"},
    {"Serial": "6", "Date": "12/07/2024", "Category": "Payment issue", "Tag": "API", "GroupID": "Payment-Team"},
]


# Example usage with all columns, specifying code columns
print("Table with all columns, preserving embedded code and JSON:")
all_columns_table = create_markdown_table(data, code_columns=["Issue", "Resolution", "Context"])
print(all_columns_table)
#
# Example usage with selected columns
print("\nTable with selected columns:")
selected_columns_table = create_markdown_table(data, columns=["Serial", "Issue", "Resolution"],
                                               code_columns=["Issue", "Resolution"])
# print(selected_columns_table)

# Generate summary for the specific date range and filtered categories
start_date = "02/06/2024"
end_date = "12/07/2024"
filtered_categories = ["Access issue"]
summary = generate_summary_with_date_range(data, start_date=start_date, end_date=end_date,
                                           categories=filtered_categories)
print(selected_columns_table + "\n" + summary)
