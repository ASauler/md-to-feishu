#!/usr/bin/env python3
"""
Markdown 转飞书文档 - 完整版
参考 OpenClaw feishu-docs 插件的实现
"""

import re
import json
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
    data = resp.json()
    if data['code'] != 0:
        raise Exception(f"获取 token 失败: {data['msg']}")
    return data['tenant_access_token']

def parse_inline(text):
    """解析行内格式（粗体、斜体、代码）"""
    elements = []
    # 简化版：只处理粗体
    parts = re.split(r'(\*\*[^*]+\*\*)', text)
    for part in parts:
        if part.startswith('**') and part.endswith('**'):
            content = part[2:-2]
            elements.append({
                'text_run': {
                    'content': content,
                    'text_element_style': {'bold': True}
                }
            })
        elif part:
            elements.append({
                'text_run': {
                    'content': part,
                    'text_element_style': {}
                }
            })
    
    if not elements:
        elements.append({'text_run': {'content': text or ' ', 'text_element_style': {}}})
    
    return elements

def markdown_to_blocks(md_content):
    """将 Markdown 转换为飞书 block 结构"""
    BT = {
        'TEXT': 2, 'H1': 3, 'H2': 4, 'H3': 5, 'H4': 6, 'H5': 7, 'H6': 8,
        'BULLET': 12, 'ORDERED': 13, 'CODE': 14, 'QUOTE': 15, 'DIVIDER': 22
    }
    
    lines = md_content.split('\n')
    blocks = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # 空行
        if not line.strip():
            i += 1
            continue
        
        # 分隔线
        if re.match(r'^(-{3,}|\*{3,}|_{3,})\s*$', line.strip()):
            blocks.append({'block_type': BT['DIVIDER'], 'divider': {}})
            i += 1
            continue
        
        # 代码块
        if line.strip().startswith('```'):
            lang = line.strip()[3:].strip() or 'plain'
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i])
                i += 1
            i += 1
            
            blocks.append({
                'block_type': BT['CODE'],
                'code': {
                    'elements': [{'text_run': {'content': '\n'.join(code_lines) or ' ', 'text_element_style': {}}}],
                    'language': 1  # plain text
                }
            })
            continue
        
        # 标题
        hm = re.match(r'^(#{1,6})\s+(.+)', line)
        if hm:
            level = len(hm.group(1))
            text = hm.group(2)
            types = [0, BT['H1'], BT['H2'], BT['H3'], BT['H4'], BT['H5'], BT['H6']]
            key = ['', 'heading1', 'heading2', 'heading3', 'heading4', 'heading5', 'heading6'][level]
            blocks.append({
                'block_type': types[level],
                key: {'elements': parse_inline(text)}
            })
            i += 1
            continue
        
        # 引用
        if line.startswith('> ') or line == '>':
            text = line.replace('> ', '').replace('>', '')
            blocks.append({
                'block_type': BT['QUOTE'],
                'quote': {'elements': parse_inline(text)}
            })
            i += 1
            continue
        
        # 无序列表
        bm = re.match(r'^(\s*)[-*]\s+(.+)', line)
        if bm:
            blocks.append({
                'block_type': BT['BULLET'],
                'bullet': {'elements': parse_inline(bm.group(2))}
            })
            i += 1
            continue
        
        # 有序列表
        om = re.match(r'^(\s*)\d+\.\s+(.+)', line)
        if om:
            blocks.append({
                'block_type': BT['ORDERED'],
                'ordered': {'elements': parse_inline(om.group(2))}
            })
            i += 1
            continue
        
        # 表格 → 转换为格式化文本
        if line.strip().startswith('|') and line.strip().endswith('|'):
            table_rows = []
            while i < len(lines) and lines[i].strip().startswith('|') and lines[i].strip().endswith('|'):
                row = [c.strip() for c in lines[i].strip()[1:-1].split('|')]
                # 跳过分隔行
                if not all(re.match(r'^[-:]+$', c) for c in row):
                    table_rows.append(row)
                i += 1
            
            if table_rows:
                # 表头（粗体）
                header_text = ' | '.join([f'**{c}**' for c in table_rows[0]])
                blocks.append({
                    'block_type': BT['TEXT'],
                    'text': {'elements': parse_inline(header_text)}
                })
                # 数据行
                for row in table_rows[1:]:
                    row_text = ' | '.join(row)
                    blocks.append({
                        'block_type': BT['TEXT'],
                        'text': {'elements': parse_inline(row_text)}
                    })
            continue
        
        # 普通段落
        blocks.append({
            'block_type': BT['TEXT'],
            'text': {'elements': parse_inline(line)}
        })
        i += 1
    
    return blocks

def create_feishu_doc(title, md_content, folder_token=None):
    """创建飞书文档并写入内容"""
    token = get_tenant_token()
    
    # 默认文件夹（Vigil Workspace）
    if not folder_token:
        folder_token = 'WXlhf1wxTlfhS2dZs7QcUO0ln3d'
    
    # 1. 创建文档
    print(f"创建文档: {title}")
    create_resp = requests.post(
        'https://open.feishu.cn/open-apis/docx/v1/documents',
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        },
        json={'title': title, 'folder_token': folder_token}
    )
    
    create_data = create_resp.json()
    if create_data['code'] != 0:
        raise Exception(f"创建文档失败: {create_data.get('msg', create_data)}")
    
    doc_id = create_data['data']['document']['document_id']
    doc_url = f"https://feishu.cn/docx/{doc_id}"
    print(f"✓ 文档已创建: {doc_url}")
    
    # 2. 转换 Markdown 为 blocks
    blocks = markdown_to_blocks(md_content)
    print(f"转换为 {len(blocks)} 个 block")
    
    # 3. 逐个插入 block（关键：直接插入到 doc_id 下，index 从 0 开始）
    print(f"写入内容...")
    inserted = 0
    failed = 0
    
    for idx, block in enumerate(blocks):
        resp = requests.post(
            f'https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/{doc_id}/children',
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            },
            json={'children': [block], 'index': -1}  # -1 表示追加到末尾
        )
        
        data = resp.json()
        if data['code'] == 0:
            inserted += 1
            if (idx + 1) % 10 == 0:
                print(f"  已写入 {idx + 1}/{len(blocks)}")
        else:
            failed += 1
            print(f"  Block {idx} 失败: {data.get('msg', data)}")
            print(f"    Block 内容: {json.dumps(block, ensure_ascii=False)[:200]}")
        
        time.sleep(0.15)  # 避免频率限制
    
    print(f"\n✓ 完成！")
    print(f"  成功: {inserted} 个 block")
    print(f"  失败: {failed} 个 block")
    print(f"  查看文档: {doc_url}")
    
    return doc_url

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("用法: python3 md_to_feishu.py <md_file> <doc_title> [folder_token]")
        print("\n示例:")
        print("  python3 md_to_feishu.py report.md '调研报告'")
        sys.exit(1)
    
    md_file = sys.argv[1]
    doc_title = sys.argv[2]
    folder_token = sys.argv[3] if len(sys.argv) > 3 else None
    
    if not os.path.exists(md_file):
        print(f"错误: 文件不存在: {md_file}")
        sys.exit(1)
    
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    try:
        url = create_feishu_doc(doc_title, content, folder_token)
        print(f"\n成功！文档 URL: {url}")
    except Exception as e:
        print(f"\n失败: {e}")
        sys.exit(1)
