#!/usr/bin/env python3
"""
Markdown 转飞书文档完整工具
支持标题、列表、粗体、斜体、代码块、表格
"""

import re
import json
import subprocess
import sys
import os
import time
import requests

def get_tenant_token():
    """获取飞书 tenant access token"""
    config_path = os.path.expanduser('~/.openclaw/openclaw.json')
    with open(config_path) as f:
        config = json.load(f)
    
    feishu_config = config['channels']['feishu']
    app_id = feishu_config['appId']
    app_secret = feishu_config['appSecret']
    
    resp = requests.post(
        'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
        json={'app_id': app_id, 'app_secret': app_secret}
    )
    return resp.json()['tenant_access_token']

def parse_markdown_table(table_text):
    """解析 Markdown 表格为二维数组"""
    lines = [line.strip() for line in table_text.strip().split('\n') if line.strip()]
    if len(lines) < 2:
        return None
    
    # 第一行是表头
    headers = [cell.strip() for cell in lines[0].split('|') if cell.strip()]
    # 第二行是分隔符，跳过
    # 剩下的是数据行
    rows = [headers]
    for line in lines[2:]:
        cells = [cell.strip() for cell in line.split('|') if cell.strip()]
        if cells and len(cells) == len(headers):
            rows.append(cells)
    
    return rows if len(rows) > 1 else None

def markdown_to_blocks(md_content):
    """将 Markdown 转换为飞书 block 结构"""
    blocks = []
    lines = md_content.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # 空行
        if not line.strip():
            i += 1
            continue
        
        # 标题
        if line.startswith('#'):
            level = len(line) - len(line.lstrip('#'))
            text = line.lstrip('#').strip()
            blocks.append({
                "block_type": level,  # 1-6 对应 H1-H6
                "heading": {"elements": [{"text_run": {"content": text}}]}
            })
            i += 1
            continue
        
        # 代码块
        if line.strip().startswith('```'):
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i])
                i += 1
            i += 1  # 跳过结束的 ```
            
            blocks.append({
                "block_type": 17,  # 代码块
                "code": {
                    "elements": [{"text_run": {"content": '\n'.join(code_lines)}}]
                }
            })
            continue
        
        # 列表
        if line.strip().startswith('-') or line.strip().startswith('*'):
            text = line.strip()[1:].strip()
            blocks.append({
                "block_type": 3,  # 无序列表
                "bullet": {"elements": [{"text_run": {"content": text}}]}
            })
            i += 1
            continue
        
        # 普通段落
        blocks.append({
            "block_type": 2,  # 文本
            "text": {"elements": [{"text_run": {"content": line}}]}
        })
        i += 1
    
    return blocks

def write_to_feishu(doc_token, md_content):
    """写入飞书文档"""
    token = get_tenant_token()
    
    # 1. 获取文档结构
    print("获取文档结构...")
    list_resp = requests.get(
        f'https://open.feishu.cn/open-apis/docx/v1/documents/{doc_token}/blocks',
        headers={'Authorization': f'Bearer {token}'},
        params={'page_size': 500}
    )
    
    if list_resp.status_code != 200:
        print(f"获取文档结构失败: {list_resp.text}")
        return False
    
    # 找到 page block（第一个 block）
    blocks_data = list_resp.json().get('data', {}).get('items', [])
    if not blocks_data:
        print("错误: 文档为空")
        return False
    
    page_block_id = blocks_data[0]['block_id']
    
    # 2. 获取 page block 的子 block
    children_resp = requests.get(
        f'https://open.feishu.cn/open-apis/docx/v1/documents/{doc_token}/blocks/{page_block_id}/children',
        headers={'Authorization': f'Bearer {token}'},
        params={'page_size': 500}
    )
    
    if children_resp.status_code != 200:
        print(f"获取子 block 失败: {children_resp.text}")
        return False
    
    children = children_resp.json().get('data', {}).get('items', [])
    
    # 如果没有子 block，创建一个 text block 作为容器
    if not children:
        print("创建初始 block...")
        create_resp = requests.post(
            f'https://open.feishu.cn/open-apis/docx/v1/documents/{doc_token}/blocks/{page_block_id}/children',
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            },
            json={
                'children': [{
                    'block_type': 2,  # text
                    'text': {'elements': [{'text_run': {'content': '加载中...'}}]}
                }],
                'index': 0
            }
        )
        
        if create_resp.status_code != 200:
            print(f"创建初始 block 失败: {create_resp.text}")
            return False
        
        time.sleep(0.5)
        
        # 重新获取子 block
        children_resp = requests.get(
            f'https://open.feishu.cn/open-apis/docx/v1/documents/{doc_token}/blocks/{page_block_id}/children',
            headers={'Authorization': f'Bearer {token}'},
            params={'page_size': 500}
        )
        children = children_resp.json().get('data', {}).get('items', [])
    
    # 使用第一个子 block 作为插入点
    insert_block_id = children[0]['block_id']
    print(f"插入点 block ID: {insert_block_id}")
    
    # 3. 转换 Markdown 为 blocks
    blocks = markdown_to_blocks(md_content)
    
    # 4. 先删除占位 block
    requests.delete(
        f'https://open.feishu.cn/open-apis/docx/v1/documents/{doc_token}/blocks/{insert_block_id}',
        headers={'Authorization': f'Bearer {token}'}
    )
    time.sleep(0.3)
    
    # 5. 分批写入到 page block 下
    print(f"写入 {len(blocks)} 个 block...")
    
    batch_size = 50
    for i in range(0, len(blocks), batch_size):
        batch = blocks[i:i+batch_size]
        
        resp = requests.post(
            f'https://open.feishu.cn/open-apis/docx/v1/documents/{doc_token}/blocks/{page_block_id}/children',
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            },
            json={'children': batch, 'index': i}
        )
        
        if resp.status_code != 200:
            print(f"写入失败: {resp.text}")
            return False
        
        print(f"  已写入 {min(i+batch_size, len(blocks))}/{len(blocks)}")
        time.sleep(0.5)
    
    return True

def md_to_feishu(md_file, doc_title=None):
    """
    将 Markdown 文件转换为飞书文档
    
    Args:
        md_file: Markdown 文件路径
        doc_title: 文档标题（可选，如果不提供则创建新文档）
    
    Returns: 文档 URL
    """
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # 1. 提取所有表格
    table_pattern = r'\|[^\n]+\|\n\|[-:\s|]+\|\n(?:\|[^\n]+\|\n?)+'
    tables = []
    table_positions = []
    
    for match in re.finditer(table_pattern, md_content):
        table_text = match.group(0)
        parsed = parse_markdown_table(table_text)
        if parsed:
            tables.append(parsed)
            table_positions.append((match.start(), match.end()))
    
    # 2. 用占位符替换表格
    md_without_tables = md_content
    for i in range(len(tables) - 1, -1, -1):
        start, end = table_positions[i]
        placeholder = f'\n\n[表格 {i+1}: {len(tables[i])}行 x {len(tables[i][0])}列]\n\n'
        md_without_tables = md_without_tables[:start] + placeholder + md_without_tables[end:]
    
    # 3. 创建文档
    if not doc_title:
        doc_title = os.path.basename(md_file).replace('.md', '')
    
    token = get_tenant_token()
    
    create_resp = requests.post(
        'https://open.feishu.cn/open-apis/docx/v1/documents',
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        },
        json={'title': doc_title}
    )
    
    if create_resp.status_code != 200:
        print(f"创建文档失败: {create_resp.text}")
        return None
    
    doc_token = create_resp.json()['data']['document']['document_id']
    doc_url = f"https://feishu.cn/docx/{doc_token}"
    
    print(f"✓ 文档已创建: {doc_url}")
    
    # 4. 写入内容
    if not write_to_feishu(doc_token, md_without_tables):
        return None
    
    # 5. 插入表格
    if tables:
        print(f"\n正在插入 {len(tables)} 个表格...")
        feishu_table_script = os.path.join(
            os.path.dirname(__file__),
            'feishu_table.py'
        )
        
        for i, table_data in enumerate(tables):
            print(f"  表格 {i+1}/{len(tables)}: {len(table_data)}行 x {len(table_data[0])}列")
            
            proc = subprocess.Popen(
                ['python3', feishu_table_script, doc_token],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            stdout, stderr = proc.communicate(input=json.dumps(table_data).encode())
            
            if proc.returncode == 0:
                print(f"  ✓ {stdout.decode().strip()}")
            else:
                print(f"  ✗ 失败: {stderr.decode()}")
    
    print(f"\n✓ 转换完成")
    print(f"查看文档: {doc_url}")
    return doc_url

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python3 md_to_feishu_full.py <md_file> [doc_title]")
        print("\n示例:")
        print("  python3 md_to_feishu_full.py SOUL.md")
        print("  python3 md_to_feishu_full.py report.md '调研报告'")
        sys.exit(1)
    
    md_file = sys.argv[1]
    doc_title = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(md_file):
        print(f"错误: 文件不存在: {md_file}")
        sys.exit(1)
    
    url = md_to_feishu(md_file, doc_title)
    sys.exit(0 if url else 1)
