# md-to-feishu

Convert Markdown files to Feishu (Lark) documents with **full native table support**.

## What This Skill Does

This skill provides tools to convert Markdown content to Feishu documents, including proper handling of tables using Feishu's native table API (block_type 31).

## Key Features

- Complete Markdown support (headings, lists, bold, italic, code blocks)
- Native Feishu table rendering (not plain text)
- Batch conversion capability
- No LLM required - pure API-based conversion

## Why It Matters

Feishu's document API doesn't natively support Markdown tables. This is the **first open-source tool** that correctly implements Feishu table creation via API.

## Tools Included

### `feishu_table.py`
Core table creation utility using Feishu native API.

**Usage**:
```bash
echo '[["Header1","Header2"],["Data1","Data2"]]' | python3 feishu_table.py <doc_token>
```

### `md_to_feishu_full.py`
Complete Markdown to Feishu converter.

**Usage**:
```bash
python3 md_to_feishu_full.py <md_file> <doc_token>
```

## Configuration

Requires Feishu app credentials with document permissions:
- Set `FEISHU_APP_ID` and `FEISHU_APP_SECRET` environment variables
- Or use OpenClaw config (automatically reads from `~/.openclaw/openclaw.json`)

## Use Cases

- Convert documentation to Feishu for team collaboration
- Migrate Markdown notes to Feishu workspace
- Automate report generation in Feishu
- Sync GitHub README to Feishu docs

## Technical Details

The tool works by:
1. Parsing Markdown tables into structured data
2. Creating empty table blocks via Feishu API
3. Fetching auto-generated cell block IDs
4. Updating each cell with content

See [README.md](README.md) for complete API reference and examples.

## Validation

Run `npm run validate` to verify installation.

## License

MIT

## Credits

Created by Vigil (OpenClaw Chief of Staff) for efficient Markdown-to-Feishu workflows.