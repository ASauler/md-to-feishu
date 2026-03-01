# Markdown to Feishu Docs Converter

[English](#english) | [中文](#中文)

---

## English

A complete toolkit for converting Markdown files to Feishu (Lark) documents, with **full table support** using native Feishu API.

### Features

- ✅ **Complete Markdown support**: Headings, lists, bold, italic, code blocks
- ✅ **Native table rendering**: Uses Feishu's native table API (not plain text)
- ✅ **Batch conversion**: Convert multiple files at once
- ✅ **Preserves formatting**: Maintains document structure and styling
- ✅ **No LLM required**: Pure API-based conversion, fast and reliable

### Why This Tool?

Feishu's document API doesn't natively support Markdown tables. This tool solves that by:
1. Parsing Markdown tables into structured data
2. Using Feishu's native table block API (block_type 31)
3. Properly formatting table cells with content

This is the **first open-source tool** that correctly implements Feishu table creation via API.

### Installation

```bash
git clone https://github.com/ASauler/md-to-feishu.git
cd md-to-feishu
pip install requests
```

### Configuration

You need a Feishu app with document permissions. Set up your credentials:

```bash
export FEISHU_APP_ID="your_app_id"
export FEISHU_APP_SECRET="your_app_secret"
```

Or use OpenClaw's config (if you're using OpenClaw):
```bash
# Config is automatically read from ~/.openclaw/openclaw.json
```

### Usage

#### Basic Conversion

```bash
# Create a new document
python3 md_to_feishu_full.py your_file.md <doc_token>
```

#### Table-Only Insertion

```bash
# Insert a table into an existing document
echo '[["Header1","Header2"],["Data1","Data2"]]' | python3 feishu_table.py <doc_token>
```

### API Reference

#### `feishu_table.py`

Core table creation utility.

**Function**: `create_table(doc_token, rows, index=-1, header_bold=True)`

**Parameters**:
- `doc_token`: Feishu document token
- `rows`: 2D array, e.g., `[["Industry","Job"],["Manufacturing","Buyer"]]`
- `index`: Insert position (-1 for end)
- `header_bold`: Whether to bold the first row

**Returns**: Table block_id or None

**Example**:
```python
from feishu_table import create_table

rows = [
    ["Name", "Age", "City"],
    ["Alice", "25", "Beijing"],
    ["Bob", "30", "Shanghai"]
]

table_id = create_table("your_doc_token", rows)
```

#### `md_to_feishu_full.py`

Complete Markdown to Feishu converter.

**Usage**:
```bash
python3 md_to_feishu_full.py <md_file> <doc_token>
```

**What it does**:
1. Parses Markdown content
2. Extracts tables
3. Converts non-table content to Feishu blocks
4. Inserts tables using native API

### How It Works

#### Table Creation Process

1. **Create empty table block**:
```json
{
  "block_type": 31,
  "table": {
    "property": {
      "row_size": 3,
      "column_size": 2
    }
  }
}
```

2. **Feishu auto-generates cell blocks**

3. **Fetch cell block IDs**:
```python
GET /docx/v1/documents/{doc_token}/blocks?page_size=500
```

4. **Update each cell**:
```python
PATCH /docx/v1/documents/{doc_token}/blocks/{cell_id}
{
  "update_text_elements": {
    "elements": [{"text_run": {"content": "Cell content"}}]
  }
}
```

### Limitations

- Feishu API rate limits apply (sleep 0.15s between cell updates)
- Maximum table size: depends on your Feishu plan
- Nested tables not supported

### Contributing

PRs welcome! Especially for:
- Markdown extensions (footnotes, task lists)
- Performance optimizations
- Better error handling

### License

MIT

---

## 中文

将 Markdown 文件转换为飞书文档的完整工具包，**完整支持表格**（使用飞书原生 API）。

### 功能特性

- ✅ **完整 Markdown 支持**：标题、列表、粗体、斜体、代码块
- ✅ **原生表格渲染**：使用飞书原生表格 API（不是纯文本）
- ✅ **批量转换**：一次转换多个文件
- ✅ **保留格式**：维持文档结构和样式
- ✅ **无需 LLM**：纯 API 转换，快速可靠

### 为什么需要这个工具？

飞书文档 API 原生不支持 Markdown 表格。本工具通过以下方式解决：
1. 解析 Markdown 表格为结构化数据
2. 使用飞书原生表格块 API (block_type 31)
3. 正确格式化表格单元格内容

这是**第一个正确实现飞书表格 API 的开源工具**。

### 安装

```bash
git clone https://github.com/ASauler/md-to-feishu.git
cd md-to-feishu
pip install requests
```

### 配置

需要一个有文档权限的飞书应用。设置凭证：

```bash
export FEISHU_APP_ID="你的_app_id"
export FEISHU_APP_SECRET="你的_app_secret"
```

或使用 OpenClaw 配置（如果你在用 OpenClaw）：
```bash
# 自动从 ~/.openclaw/openclaw.json 读取配置
```

### 使用方法

#### 基础转换

```bash
# 创建新文档
python3 md_to_feishu_full.py 你的文件.md <doc_token>
```

#### 仅插入表格

```bash
# 在现有文档中插入表格
echo '[["表头1","表头2"],["数据1","数据2"]]' | python3 feishu_table.py <doc_token>
```

### API 参考

#### `feishu_table.py`

核心表格创建工具。

**函数**: `create_table(doc_token, rows, index=-1, header_bold=True)`

**参数**:
- `doc_token`: 飞书文档 token
- `rows`: 二维数组，例如 `[["行业","职业"],["制造业","采购"]]`
- `index`: 插入位置（-1 为末尾）
- `header_bold`: 第一行是否加粗

**返回**: 表格 block_id 或 None

**示例**:
```python
from feishu_table import create_table

rows = [
    ["姓名", "年龄", "城市"],
    ["张三", "25", "北京"],
    ["李四", "30", "上海"]
]

table_id = create_table("你的_doc_token", rows)
```

### 工作原理

#### 表格创建流程

1. **创建空表格块**:
```json
{
  "block_type": 31,
  "table": {
    "property": {
      "row_size": 3,
      "column_size": 2
    }
  }
}
```

2. **飞书自动生成单元格块**

3. **获取单元格块 ID**:
```python
GET /docx/v1/documents/{doc_token}/blocks?page_size=500
```

4. **更新每个单元格**:
```python
PATCH /docx/v1/documents/{doc_token}/blocks/{cell_id}
{
  "update_text_elements": {
    "elements": [{"text_run": {"content": "单元格内容"}}]
  }
}
```

### 限制

- 飞书 API 速率限制（单元格更新间隔 0.15 秒）
- 最大表格大小：取决于你的飞书套餐
- 不支持嵌套表格

### 贡献

欢迎 PR！特别是：
- Markdown 扩展（脚注、任务列表）
- 性能优化
- 更好的错误处理

### 许可证

MIT

---

## Credits

Created by Vigil (OpenClaw Chief of Staff) for Saul.

Part of the Vigil workspace automation toolkit.