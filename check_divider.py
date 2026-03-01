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

# 检查刚才创建的文档
doc_id = 'Iql8dKx6BoQUrPx2ZYlcdXkNnig'  # 第一个完整报告

resp = requests.get(
    f'https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks',
    headers={'Authorization': f'Bearer {token}'},
    params={'page_size': 500}
)

blocks = resp.json()['data']['items']
print(f"文档总共有 {len(blocks)} 个 block")

# 查找 divider
dividers = [b for b in blocks if b.get('block_type') == 27]
print(f"Divider 数量: {len(dividers)}")

# 查看前几个 block 的类型
print("\n前 20 个 block 类型:")
for i, b in enumerate(blocks[:20]):
    print(f"  {i}: type={b.get('block_type')}")
