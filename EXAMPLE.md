# Example: Converting a Markdown file with tables to Feishu

This example demonstrates how to convert a Markdown file containing tables to a Feishu document.

## Input: sample.md

```markdown
# Project Report

## Overview

This is a sample report with a table.

## Team Members

| Name | Role | Location |
|------|------|----------|
| Alice | Engineer | Beijing |
| Bob | Designer | Shanghai |
| Carol | PM | Shenzhen |

## Status

- Project is on track
- Next milestone: March 15
```

## Usage

```bash
# 1. Create a new Feishu document first (get the doc_token)
# 2. Run the converter
python3 md_to_feishu_full.py sample.md <your_doc_token>
```

## Output

The tool will:
1. Parse the Markdown content
2. Extract the table
3. Convert headings, lists, and text to Feishu blocks
4. Insert the table using native Feishu table API

## Result

You'll get a properly formatted Feishu document with:
- Heading 1: "Project Report"
- Heading 2: "Overview"
- Paragraph: "This is a sample report with a table."
- Heading 2: "Team Members"
- **Native Feishu table** with 3 columns and 4 rows (including header)
- Heading 2: "Status"
- Bullet list with 2 items

## Table Details

The table will be rendered as a native Feishu table block, not plain text:
- Header row is bold
- Cells are properly aligned
- You can edit the table directly in Feishu after creation

## Python API Example

```python
from feishu_table import create_table

# Define your table data
team_table = [
    ["Name", "Role", "Location"],
    ["Alice", "Engineer", "Beijing"],
    ["Bob", "Designer", "Shanghai"],
    ["Carol", "PM", "Shenzhen"]
]

# Create the table
doc_token = "your_feishu_doc_token"
table_id = create_table(doc_token, team_table)

print(f"Table created with ID: {table_id}")
```

## Advanced: Multiple Tables

If your Markdown has multiple tables, they'll all be converted:

```markdown
# Q1 Report

## Sales by Region

| Region | Revenue |
|--------|---------|
| North  | $100K   |
| South  | $150K   |

## Expenses

| Category | Amount |
|----------|--------|
| Marketing| $50K   |
| R&D      | $80K   |
```

Both tables will be inserted as native Feishu tables in the correct positions.