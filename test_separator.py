import requests
import json
import os
import time

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
token = resp.json()['tenant_access_token']

# 创建测试文档
create_resp = requests.post(
    'https://open.feishu.cn/open-apis/docx/v1/documents',
    headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
    json={'title': '分隔符测试'}
)
doc_id = create_resp.json()['data']['document']['document_id']
print(f"文档创建: https://feishu.cn/docx/{doc_id}")

# 测试不同的分隔方式
tests = [
    # 1. 空文本 block
    {'name': '空文本', 'block': {'block_type': 2, 'text': {'elements': [{'text_run': {'content': ' ', 'text_element_style': {}}}]}}},
    
    # 2. 引用 block（空内容）
    {'name': '空引用', 'block': {'block_type': 15, 'quote': {'elements': [{'text_run': {'content': ' ', 'text_element_style': {}}}]}}},
    
    # 3. 代码 block（只有横线）
    {'name': '代码横线', 'block': {'block_type': 14, 'code': {'elements': [{'text_run': {'content': '─' * 50, 'text_element_style': {}}}], 'language': 1}}},
    
    # 4. 引用 block（横线）
    {'name': '引用横线', 'block': {'block_type': 15, 'quote': {'elements': [{'text_run': {'content': '─' * 50, 'text_element_style': {}}}]}}},
]

for test in tests:
    resp = requests.post(
        f'https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/{doc_id}/children',
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
        json={'children': [test['block']], 'index': -1}
    )
    result = resp.json()
    status = '✓' if result['code'] == 0 else '✗'
    print(f"{status} {test['name']}: {result.get('msg', 'success')}")
    time.sleep(0.2)

print(f"\n查看效果: https://feishu.cn/docx/{doc_id}")
