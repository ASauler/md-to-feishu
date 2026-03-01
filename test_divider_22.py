import requests
import json
import os

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
    json={'title': 'Divider Type 22 测试'}
)
doc_id = create_resp.json()['data']['document']['document_id']
print(f"文档创建: https://feishu.cn/docx/{doc_id}")

# 测试 type 22 的 divider
divider_block = {'block_type': 22, 'divider': {}}
resp = requests.post(
    f'https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/{doc_id}/children',
    headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
    json={'children': [divider_block], 'index': -1}
)

result = resp.json()
print(f"结果: {result}")
if result['code'] == 0:
    print("✓ 成功！Type 22 是正确的")
else:
    print(f"✗ 失败: {result.get('msg')}")
