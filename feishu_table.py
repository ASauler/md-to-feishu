#!/usr/bin/env python3
"""飞书文档表格创建工具 - 通过 API 在飞书文档中插入原生表格"""

import json, requests, time, sys

def get_token():
    conf = json.load(open('/home/moltbot/.openclaw/openclaw.json'))
    app_id = conf['channels']['feishu']['appId']
    app_secret = conf['channels']['feishu']['appSecret']
    r = requests.post('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
        json={"app_id": app_id, "app_secret": app_secret})
    return r.json()['tenant_access_token']

def create_table(doc_token, rows, index=-1, header_bold=True):
    """
    在飞书文档中创建表格
    
    Args:
        doc_token: 文档 token
        rows: 二维数组，如 [["行业","代表职业"],["制造业","采购代理"]]
        index: 插入位置（-1 为末尾）
        header_bold: 第一行是否加粗
    
    Returns: table block_id or None
    """
    token = get_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    row_size = len(rows)
    col_size = len(rows[0]) if rows else 0
    if row_size == 0 or col_size == 0:
        print("Error: empty table data")
        return None

    # 1. 创建空表格
    data = {
        "children": [{"block_type": 31, "table": {"property": {"row_size": row_size, "column_size": col_size}}}],
        "index": index
    }
    r = requests.post(f'https://open.feishu.cn/open-apis/docx/v1/documents/{doc_token}/blocks/{doc_token}/children',
        headers=headers, json=data)
    result = r.json()
    if result.get('code') != 0:
        print(f"Error creating table: {result.get('msg')}")
        return None

    table_block = result['data']['children'][0]
    table_id = table_block['block_id']
    cells = table_block['table']['cells']

    # 2. 获取 cell 内的 text block ids
    time.sleep(0.3)
    r2 = requests.get(f'https://open.feishu.cn/open-apis/docx/v1/documents/{doc_token}/blocks?page_size=500', headers=headers)
    all_blocks = {b['block_id']: b for b in r2.json()['data']['items']}

    # 3. 填充内容（cells 按行优先排列）
    flat_data = [cell for row in rows for cell in row]
    for i, cell_id in enumerate(cells):
        cell_block = all_blocks.get(cell_id)
        if cell_block and cell_block.get('children'):
            text_bid = cell_block['children'][0]
            is_header = header_bold and (i < col_size)
            elements = [{"text_run": {"content": flat_data[i], "text_element_style": {"bold": is_header}}}]
            update = {"update_text_elements": {"elements": elements}}
            time.sleep(0.15)
            r3 = requests.patch(f'https://open.feishu.cn/open-apis/docx/v1/documents/{doc_token}/blocks/{text_bid}',
                headers=headers, json=update)
            try:
                if r3.json().get('code') != 0:
                    print(f"  Cell[{i}] error: {r3.json().get('msg','')[:60]}")
            except:
                print(f"  Cell[{i}] request error: {r3.status_code}")

    print(f"Table created: {row_size}x{col_size}, block_id={table_id}")
    return table_id

if __name__ == "__main__":
    # 示例用法
    if len(sys.argv) < 2:
        print("Usage: python3 feishu_table.py <doc_token> [index]")
        print("  Reads JSON table data from stdin: [[\"h1\",\"h2\"],[\"r1c1\",\"r1c2\"]]")
        sys.exit(1)
    
    doc_token = sys.argv[1]
    index = int(sys.argv[2]) if len(sys.argv) > 2 else -1
    rows = json.load(sys.stdin)
    create_table(doc_token, rows, index=index)
