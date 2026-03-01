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
        if cells and len(cells) == len(headers):  # 确保列数一致
            rows.append(cells)
    
    return rows if len(rows) > 1 else None

def md_to_feishu(md_file, doc_token):
    """
    将 Markdown 文件转换为飞书文档
    
    Args:
        md_file: Markdown 文件路径
        doc_token: 飞书文档 token
    
    Returns: 成功返回 True
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
    for i in range(len(tables) - 1, -1, -1):  # 从后往前替换，避免位置偏移
        start, end = table_positions[i]
        placeholder = f'\n\n**[表格 {i+1}: {len(tables[i])}行 x {len(tables[i][0])}列]**\n\n'
        md_without_tables = md_without_tables[:start] + placeholder + md_without_tables[end:]
    
    # 3. 写入文档内容（调用 OpenClaw feishu_doc 工具）
    print(f"正在写入文档内容...")
    
    # 将内容写入临时文件，避免命令行参数长度限制
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as tmp:
        tmp.write(md_without_tables)
        tmp_path = tmp.name
    
    try:
        # 读取内容并通过 stdin 传递
        proc = subprocess.Popen(
            ['openclaw', 'run', '--', f'用 feishu_doc 工具的 write action 更新文档 {doc_token}，内容从文件 {tmp_path} 读取'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = proc.communicate(timeout=60)
        
        if proc.returncode != 0:
            print(f"写入文档失败: {stderr.decode()}")
            # 降级方案：直接用 Python 调用 API
            print("尝试直接调用 API...")
            if not write_via_api(doc_token, md_without_tables):
                return False
        
        print(f"✓ 文档内容写入成功")
        
    finally:
        os.unlink(tmp_path)
    
    # 4. 插入表格
    if tables:
        print(f"\n正在插入 {len(tables)} 个表格...")
        feishu_table_script = os.path.join(
            os.path.dirname(__file__),
            'feishu_table.py'
        )
        
        for i, table_data in enumerate(tables):
            print(f"  表格 {i+1}/{len(tables)}: {len(table_data)}行 x {len(table_data[0])}列")
            
            # 调用 feishu_table.py
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
    print(f"查看文档: https://feishu.cn/docx/{doc_token}")
    return True

def write_via_api(doc_token, content):
    """直接通过 API 写入文档（降级方案）"""
    try:
        import requests
        
        # 获取 token
        config_path = os.path.expanduser('~/.openclaw/openclaw.json')
        with open(config_path) as f:
            config = json.load(f)
        
        feishu_config = config['channels']['feishu']
        app_id = feishu_config['appId']
        app_secret = feishu_config['appSecret']
        
        token_resp = requests.post(
            'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
            json={'app_id': app_id, 'app_secret': app_secret}
        )
        token = token_resp.json()['tenant_access_token']
        
        # 这里需要实现完整的 Markdown 转飞书 block 的逻辑
        # 暂时简化：只写纯文本
        print("API 直接写入暂未实现，请使用 OpenClaw feishu_doc 工具")
        return False
        
    except Exception as e:
        print(f"API 写入失败: {e}")
        return False

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("用法: python3 md_to_feishu_full.py <md_file> <doc_token>")
        print("\n示例:")
        print("  python3 md_to_feishu_full.py SOUL.md KQQMdES3vowNhbxHhIoczRDjnEd")
        sys.exit(1)
    
    md_file = sys.argv[1]
    doc_token = sys.argv[2]
    
    if not os.path.exists(md_file):
        print(f"错误: 文件不存在: {md_file}")
        sys.exit(1)
    
    success = md_to_feishu(md_file, doc_token)
    sys.exit(0 if success else 1)
