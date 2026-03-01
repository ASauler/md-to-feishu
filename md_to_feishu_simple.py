#!/usr/bin/env python3
"""
Markdown 转飞书文档 - 简化版
使用 OpenClaw 的 feishu_doc 工具
"""

import sys
import os
import subprocess
import json

def md_to_feishu_simple(md_file, doc_title):
    """
    使用 OpenClaw feishu_doc 工具转换 Markdown
    
    Args:
        md_file: Markdown 文件路径
        doc_title: 文档标题
    
    Returns: 文档 URL
    """
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. 创建文档
    print(f"创建文档: {doc_title}")
    
    # 使用 Python 直接调用 feishu_doc 工具
    # 这需要在 OpenClaw session 中运行
    
    # 临时方案：输出 JSON，让用户手动调用
    output = {
        "action": "create_and_write",
        "title": doc_title,
        "content": content,
        "instruction": f"请在 OpenClaw 中运行:\n\nfeishu_doc(action='create', title='{doc_title}', content='''占位''')\n然后用返回的 doc_token 运行:\nfeishu_doc(action='write', doc_token='<token>', content='''<从 {md_file} 读取的内容>''')"
    }
    
    print(json.dumps(output, ensure_ascii=False, indent=2))
    
    print(f"\n由于 md-to-feishu 工具需要在 OpenClaw session 中运行，")
    print(f"请直接告诉 Vigil：")
    print(f"\n用 feishu_doc 工具把 {md_file} 转成飞书文档，标题是 {doc_title}")
    
    return None

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("用法: python3 md_to_feishu_simple.py <md_file> <doc_title>")
        sys.exit(1)
    
    md_file = sys.argv[1]
    doc_title = sys.argv[2]
    
    if not os.path.exists(md_file):
        print(f"错误: 文件不存在: {md_file}")
        sys.exit(1)
    
    md_to_feishu_simple(md_file, doc_title)
